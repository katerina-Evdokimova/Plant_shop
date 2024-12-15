from flask import render_template, request
from flask import jsonify
from app import app
from data import db_session
from data.users import User
from data.plant import Plant
from data.client import Client
from data.admin import Admin
from data.order import Order
from login_manager import *
from query_bd import *
from datetime import datetime
import sqlalchemy as sa

# Настройки для пагинации
PER_PAGE = 10

def format_datetime(dt):
    # Проверяем, если дата уже объект datetime
    if not isinstance(dt, str):
        return dt.strftime("%d.%m.%Y %H:%M")
    
    # Если дата в строковом формате, пытаемся конвертировать её
    print(type(dt))
    try:
        dt = datetime.fromisoformat(dt)
        return dt.strftime("%d.%m.%y %H:%M")
    except ValueError:
        return "Неверный формат даты"
    

@app.route('/api/total_pages')
def get_total_pages():
    name_table = request.args.get('name', '')

    db_sess = db_session.create_session()
    title, table_data = get_table_data_by_type(db_sess, name_table)
    total_pages = (len(table_data) + PER_PAGE - 1) // PER_PAGE
    return jsonify({"total_pages": total_pages})

@app.route('/api/table_data')
def get_table_data():
    name_table = request.args.get('name', '')
    print(1)
    # Извлекаем параметры сортировки из запроса
    sort_config = {}
    for key, value in request.args.items():
        if key.startswith('sort_'):
            column_index = int(key.split('_')[1])
            sort_config[column_index] = value


    data = get_sorted_data(name_table, sort_config)
    # print(data)

    db_sess = db_session.create_session()

    title, table_data = get_table_data_by_type(db_sess, name_table, data)
    
    # Получаем список ролей для каждого пользователя
    if name_table == 'users':
        print(table_data)
        role_data = {user['id']: ', '.join(get_user_role(db_sess, user['id'])) for user in table_data}
        print(role_data)
        # Применяем сортировку к данным
        for column_index, direction in sort_config.items():
            if column_index == 9:  # Индекс колонки с ролями
                reverse = direction == 'desc'
                # Сортируем по ролям, используя role_data для каждого user
                table_data.sort(key=lambda x: role_data.get(x['id'], ''), reverse=reverse)

    page = int(request.args.get('page', 1))
    start = (page - 1) * PER_PAGE
    end = start + PER_PAGE
    items = table_data[start:end]
    print(items)
    return jsonify({"items": items})

@app.route('/api/update_role', methods=['POST'])
def update_role():
    data = request.json
    user_id = data.get("userId")
    role = data.get("role")
    is_adding = data.get("isAdding")

    if not user_id or not role:
        return jsonify({"error": "Некорректные данные"}), 400

    db_sess = db_session.create_session()
    # Получаем пользователя по user_id
    user = db_sess.query(User).filter_by(id=user_id).first()

    if user:
        # Проверяем, имеет ли администратор права изменять роль
        if role == "Admin" and current_user.id == user.id:
            return jsonify({"error": "Нельзя изменять свою собственную роль"}), 403

        # Логика добавления или удаления роли
        if is_adding:
            # Добавляем роль в нужную таблицу
            add_role_to_user(user, role)
        else:
            # Удаляем роль из таблицы
            remove_role_from_user(user, role)

        db_sess.commit()
        return jsonify({"success": True})
    else:
        return jsonify({"error": "Пользователь не найден"}), 404
    
@app.route('/api/product_data')
def product_data():
    return jsonify(get_product_data())

@app.route('/api/user_data')
def user_data():
    return jsonify(get_user_data())

@app.route('/api/recent_activity')
def recent_activity():
    return jsonify(get_recent_activity())

@app.route('/api/order_statuses')
def order_statuses():
    return jsonify(get_order_statuses())

@app.route('/api/update_status', methods=['POST'])
def update_status():
    data = request.json
    # print(data)

    order_id = data.get('orderId')
    new_status = data.get('newStatus')

    if not order_id or not new_status:
        return jsonify({"error": "Invalid data"}), 400

    # Обновляем данные в базе
    db_sess = db_session.create_session()
    order = db_sess.query(Order).filter_by(id=order_id).first()
    if not order:
        return jsonify({"error": "Order not found"}), 404
    print(order)
    order.status = new_status
    order.date = sa.func.current_timestamp()
    
    print(order)

    db_sess.commit()

    # print(f"Order {order_id} updated to {new_status}")  # Для отладки
    return jsonify({"success": True, "message": "Status updated"}), 200


@app.route('/api/top_products')
def top_products():
    return jsonify(get_top_products())

@app.route('/api/update_item_field', methods=['POST'])
def update_item():
    print('!!!!')
    data = request.json
    print(data)

    id_plant = data.get('id')
    field = data.get('field')
    value = data.get('value')

    if not id_plant or not field or not value:
        return jsonify({"error": "Invalid data"}), 400
    
    # Обновляем данные в базе
    db_sess = db_session.create_session()
    plant = db_sess.query(Plant).filter_by(id=id_plant).first()
    if not plant:
        return jsonify({"error": "Plant not found"}), 404
    print(plant)
    if field == 'Количество':
        plant.quantity = int(value)
    elif field == 'Цена':
        plant.price = float(value)
    elif field == 'Скидка':
        if int(value) < 97:
            plant.sale = int(value)
        else:
            return jsonify({"success": False, "message": "Sale > 97!!"}), 400

    print("edit: ", plant)

    db_sess.commit()

    # print(f"Order {order_id} updated to {new_status}")  # Для отладки
    return jsonify({"success": True, "message": "Status updated"}), 200


def get_table_data_by_type(session, name_table: str, data=None):
    # Заголовки столбцов для каждой таблицы
    titles = {
        'plants': ["id", "Название", "Категория", "Цена", "Количество", "Скидка"],
        'users': ["id", "Логин", "Почта", "Телефон", "Пол", "Имя", "Фамилия", "Дата рождения", "Дата регистрации", "Роль"],
        'orders': ["Номер заказа", "id клиента", "Статус", "Метод оплаты", "Адрес", "Дата последнего изменения"]
    }
    
    # Выбор модели в зависимости от имени таблицы
    if name_table == 'plants':
        if not data:
            data = session.query(Plant).all()
        result = [
            {
               titles['plants'][0]: plant.id,
               titles['plants'][1]: plant.name,
               titles['plants'][2]: plant.category.name if plant.category else 'Нет категории',
               titles['plants'][3]: plant.price,
               titles['plants'][4]: plant.quantity,
               titles['plants'][5]: plant.sale,
               "href": f"plants/{plant.id}"
            }
            for plant in data
        ]
    
    elif name_table == 'users':
        if not data:
            data = session.query(User).all()
        result = [
            {
                titles[name_table][0]: user.id,
                titles[name_table][1]: user.login,
                titles[name_table][2]: user.email,
                titles[name_table][3]: user.phone,
                titles[name_table][4]: user.gender,
                titles[name_table][5]: user.first_name,
                titles[name_table][6]: user.last_name,
                titles[name_table][7]: format_datetime(user.birth_date),
                titles[name_table][8]: format_datetime(user.registration_date),
                titles[name_table][9]: get_user_role(session, user.id),
                "href": f"users/{user.id}"
            }
            for user in data
        
        ]

    
    elif name_table == 'orders':
        if not data:
            data = session.query(Order).all()
        result = [
            {
                titles[name_table][0]: order.id,
                titles[name_table][1]: order.client_id,
                titles[name_table][2]: order.status,
                titles[name_table][3]: order.payment_method,
                titles[name_table][4]: order.address,
                titles[name_table][5]: format_datetime(order.date),
                "href": f"/orders/{order.id}"
            }
            for order in data
        ]
    else:
        raise ValueError("Unsupported table name")
    
    # Возвращаем заголовки и данные
    return titles.get(name_table, []), result

def get_user_role(session, user_id: int):
    """
    Функция для определения роли пользователя.
    """
    answer = []
    if session.query(Client).filter_by(user_id=user_id).first():
        answer.append('Клиент')
    if session.query(Admin).filter_by(user_id=user_id).first():
        answer.append('Админ')
    if session.query(Supplier).filter_by(user_id=user_id).first():
        answer.append('Поставщик')
    if session.query(Seller).filter_by(user_id=user_id).first():
        answer.append('Продавец')
    return ['Неизвестная роль'] if not answer else answer
