from flask import render_template, redirect, url_for, request, flash, session
from flask import jsonify
from app import app
from data import db_session
from query_bd import get_plant_by_id, get_popular_plants, is_admin
from login_manager import *

@app.route('/')
@app.route('/index')
def home():
    db_sess = db_session.create_session()
    products = get_popular_plants(db_sess)
    try:
        return render_template('index.html', current_user=current_user, products=products, session=session, n=6, admin=is_admin(db_sess, current_user.id))
    except AttributeError:
        return render_template('index.html', current_user=current_user, products=products, session=session, n=6, admin=False)



@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    product_id = request.json.get('product_id')

    # Инициализируем корзину, если её нет
    if 'cart' not in session:
        session['cart'] = {}

    cart = session['cart']

    # Если товар уже в корзине, увеличиваем его количество
    db_sess = db_session.create_session()
    plant = get_plant_by_id(db_sess, product_id) 
    if product_id in cart:
        if plant.quantity > cart[product_id]:
            cart[product_id] += 1 
    else:
        cart[product_id] = 1  # Добавляем новый товар с количеством 1

    session.modified = True  # Обозначаем, что сессия изменена
    return jsonify(cart=cart)  # Возвращаем JSON с обновлённой корзиной


@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    product_id = request.json.get('product_id')
    print(product_id)
    # Проверяем, что корзина существует
    if 'cart' not in session:
        return jsonify(error='Корзина пуста'), 400

    cart = session['cart']

    if product_id in cart:
        cart[product_id] -= 1  # Уменьшаем количество

        if cart[product_id] <= 0:
            del cart[product_id]  # Удаляем товар из корзины, если его количество стало 0
    else:
        return jsonify(error='Товар не найден в корзине'), 400

    print(cart)
    session.modified = True  # Обозначаем, что сессия изменена
    return jsonify(cart=cart) 

@app.route('/delete_from_cart', methods=['POST'])
def delete_from_cart():
    product_id = request.json.get('plant_id')
    print(type(product_id))
    # Проверяем, что корзина существует
    if 'cart' not in session:
        return jsonify(error='Корзина пуста'), 400

    cart = session['cart']
    print(cart)
    if product_id in cart:
        del cart[product_id]
    else:
        return jsonify(error='Товар не найден в корзине'), 400

    session.modified = True  # Обозначаем, что сессия изменена
    return jsonify({'cart': cart, 'success': True})

# Маршрут для показа карточки товара
@app.route('/plant/<int:plant_id>')
def created_cart_for_plant(plant_id):
    db_sess = db_session.create_session()
    plant = get_plant_by_id(db_sess, plant_id)  # Загрузка растенияы из БД
    return render_template('card_plant.html', plant=plant, session=session, title=f'{plant.name}')
