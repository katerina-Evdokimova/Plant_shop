from sqlalchemy.orm import Session, joinedload
from sqlalchemy import case, asc, desc
from sqlalchemy.exc import NoResultFound
from data.plant import Plant
from data.users import User
from data.client import Client
from data.admin import Admin
from data.address import Address
from sqlalchemy import func
from data.order_items import OrderItem 
from data import db_session
from data.supplier import Supplier
from data.seller import Seller
from data.order import Order
from collections import Counter

def add_role_to_user(user, role):
    """
    Добавляет роль пользователю, создавая запись в соответствующей таблице.
    """
    db_sess = db_session.create_session()
    print('!!!', role)
    if role == "Админ":
        # Проверяем, есть ли уже такая роль у пользователя
        if db_sess.query(Admin).filter_by(user_id=user.id).first():
            return "Пользователь уже имеет роль Админа"
        # Добавляем роль Админа
        new_admin = Admin(user_id=user.id)
        db_sess.add(new_admin)
    
    elif role == "Клиент":
        if db_sess.query(Client).filter_by(user_id=user.id).first():
            return "Пользователь уже имеет роль Клиента"
        new_client = Client(user_id=user.id, phone=user.phone)
        db_sess.add(new_client)
    
    elif role == "Поставщик":
        if db_sess.query(Supplier).filter_by(user_id=user.id).first():
            return "Пользователь уже имеет роль Поставщика"
        new_supplier = Supplier(user_id=user.id, name=user.last_name, contact=user.phone)
        db_sess.add(new_supplier)
    
    elif role == "Продавец":
        if db_sess.query(Seller).filter_by(user_id=user.id).first():
            return "Пользователь уже имеет роль Продавца"
        new_seller = Seller(user_id=user.id, phone=user.phone)
        db_sess.add(new_seller)
    
    else:
        return "Роль не найдена"
    
    db_sess.commit()
    return "Роль успешно добавлена"

def remove_role_from_user(user, role):
    """
    Удаляет роль у пользователя, удаляя запись из соответствующей таблицы.
    """
    db_sess = db_session.create_session()

    if role == "Admin":
        role_entry = db_sess.query(Admin).filter_by(user_id=user.id).first()
        if not role_entry:
            return "Роль Админа у пользователя отсутствует"
        db_sess.delete(role_entry)
    
    elif role == "Client":
        role_entry = db_sess.query(Client).filter_by(user_id=user.id).first()
        if not role_entry:
            return "Роль Клиента у пользователя отсутствует"
        db_sess.delete(role_entry)
    
    elif role == "Supplier":
        role_entry = db_sess.query(Supplier).filter_by(user_id=user.id).first()
        if not role_entry:
            return "Роль Поставщика у пользователя отсутствует"
        db_sess.delete(role_entry)
    
    elif role == "Seller":
        role_entry = db_sess.query(Seller).filter_by(user_id=user.id).first()
        if not role_entry:
            return "Роль Продавца у пользователя отсутствует"
        db_sess.delete(role_entry)
    
    else:
        return "Роль не найдена"
    
    db_sess.commit()
    return "Роль успешно удалена"

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
            'error': status_counts.get('отклонен', 0) if status_counts.get('отклонен', 0) else status_counts.get('отклонён', 0)}

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

def get_plant_by_id(session: Session, product_id: int):
    """
    Получает данные о растении по его id.

    :param session: Объект сессии SQLAlchemy.
    :param product_id: ID растения для поиска.
    :return: Объект Plant или None, если растение не найдено.
    :raises NoResultFound: Если растение не найдено.
    """
    try:
        product = session.query(Plant).filter(Plant.id == product_id).one()
        return product
    except NoResultFound:
        return None

def get_plants(session: Session, sort_by_price: str = None):
    try:
        # Создание базового запроса
        query = session.query(Plant)
        
        # Базовая сортировка: сначала товары с большим количеством, затем товары с quantity=0 в конце
        sort_conditions = [
            case((Plant.quantity == 0, 1), else_=0),  # Товары с quantity=0 будут в конце
            Plant.quantity.desc()  # Сначала товары с большим количеством
        ]

        # Применяем все условия сортировки в один вызов order_by()
        query = query.order_by(*sort_conditions)

        # Выполняем запрос и возвращаем результат
        products = query.all()

        # Проверка на сортировку по цене
        if sort_by_price == 'asc':
            products.sort(key=lambda x: x.price * (1 - (x.sale / 100)) if x.quantity and int(x.quantity) > 0 else float('inf') )
        elif sort_by_price == 'desc':
            # Добавляем условие сортировки по убыванию цены с учётом скидки
            products.sort(key=lambda x: - x.price * (1 - (x.sale / 100)) if x.quantity and int(x.quantity) > 0 else 0)
        
        return products
    except NoResultFound:
        return None

def get_popular_plants(session: Session):

    try:
        # Выполняем запрос к базе данных с joinedload для предварительной загрузки категории
        popular_plants = session.query(
            Plant, func.sum(OrderItem.quantity).label('total_sold')
        ).join(OrderItem, Plant.id == OrderItem.plant_id) \
         .options(joinedload(Plant.category)).group_by(Plant.id) \
         .order_by(func.sum(OrderItem.quantity).desc()) \
         .all()

        # Возвращаем список растений в формате Plant
        return [plant[0] for plant in popular_plants]  # Возвращаем только объекты Plant

    finally:
        # Закрываем сессию
        session.close()

def get_client_by_id(session: Session, user_id: int):
    try:
        product = session.query(Client).filter(Client.user_id == user_id).first()
        return product
    except NoResultFound:
        return None
    
def get_address_by_id(session: Session, client_id: int):
    try:
        product = session.query(Address).filter(Address.client_id == client_id).all()
        return product
    except NoResultFound:
        return None


def delails_order_by_order_id(session: Session, order_id: int):
    order_item = session.query(OrderItem).filter(OrderItem.order_id == order_id).all()
    items = [
        {
            'id': item.id,
            'plant': get_plant_by_id(session, item.plant_id),
            'quantity': item.quantity,
            'price': item.price
        }
        for item in order_item
    ]
    return items

def is_admin(session: Session, user_id: int):
    admin = session.query(Admin).filter(Admin.user_id == user_id).first()
    return not (admin is None)

def is_seller(session: Session, user_id: int):
    seller = session.query(Seller).filter(Seller.user_id == user_id).first()
    return not (seller is None)

def is_supplier(session: Session, user_id: int):
    supplier = session.query(Supplier).filter(Supplier.user_id == user_id).first()
    return not (supplier is None)

def get_sorted_data(table_name, sort_config):
    # Извлекаем параметры сортировки из запроса

    db_sess = db_session.create_session()

    if table_name == 'users':
        query = db_sess.query(User)
    elif table_name == 'plants':
        query = db_sess.query(Plant).join(Plant.category)
    elif table_name == 'orders':
        query = db_sess.query(Order)

        
    for column_index, direction in sort_config.items():
        if column_index != 9:
            
            if direction == 'asc':
                query = query.order_by(asc(get_column_by_index(column_index, table_name)))
            elif direction == 'desc':
                query = query.order_by(desc(get_column_by_index(column_index, table_name)))

    return query.all()

# Вспомогательная функция для получения колонки по индексу
def get_column_by_index(column_index, table_name):
    if table_name == 'users':
        columns = {
            0: User.id,
            1: User.login,
            2: User.email,
            3: User.phone,
            4: User.gender,
            5: User.first_name,
            6: User.last_name,
            7: User.birth_date,
            8: User.registration_date
        }
    elif table_name == 'plants':
        columns = {
            0: Plant.name,
            1: Plant.category,
            2: Plant.price,
            3: Plant.quantity
        }
    elif table_name == 'orders':
        columns = {
            0: Order.id,
            1: Order.client_id,
            2: Order.status,
            3: Order.payment_method,
            4: Order.address,
            5: Order.date
        }
    
    return columns.get(column_index)