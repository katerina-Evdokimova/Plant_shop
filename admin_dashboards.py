from flask import Flask, jsonify, render_template
from sqlalchemy.orm import Session, joinedload
from data import db_session
from data.plant import Plant
from data.supplier import Supplier
from data.seller import Seller
from data.client import Client
from data.order import Order
from data.order_items import OrderItem
from collections import Counter
from sqlalchemy import case, asc, desc
from sqlalchemy import func


def get_product_data():
    db_sess = db_session.create_session()
    total_products = db_sess.query(Plant).count()
    out_of_stock = db_sess.query(Plant).filter(Plant.quantity == 0).count()
    return {'total': total_products, 'out_of_stock': out_of_stock}

def get_user_data():
    db_sess = db_session.create_session()
    suppliers = db_sess.query(Supplier).count()
    sellers = db_sess.query(Seller).count()
    clients = db_sess.query(Client).count()
    return {'suppliers': suppliers, 'sellers': sellers, 'clients': clients}

def get_recent_activity():
    db_sess = db_session.create_session()
    orders = db_sess.query(Order).order_by(Order.date.desc()).limit(5).all()
    return [{'id': order.id, 'status': order.status, 'date': order.date} for order in orders]

def get_order_statuses():
    db_sess = db_session.create_session()
    status_counts = Counter(order.status for order in db_sess.query(Order).all())
    return {'processing': status_counts.get('обработка', 0),
            'approved': status_counts.get('одобрен', 0),
            'error': status_counts.get('отклонен', 0)}

def get_top_products():
    db_sess = db_session.create_session()
    top_products = db_sess.query(
            Plant, func.sum(OrderItem.quantity).label('total_sold')
        ).join(OrderItem, Plant.id == OrderItem.plant_id) \
         .options(joinedload(Plant.category)) \
         .group_by(Plant.id) \
         .order_by(func.sum(OrderItem.quantity).desc()) \
         .limit(3).all()

    # Приводим данные к удобному формату для JSON-вывода
    return [
        {
            'id': product.id,
            'name': product.name,
            'image': product.picture, 
            'category': product.category.name,  # если у Plant есть категория
            'total_sold': total_sold
        }
        for product, total_sold in top_products
    ]