from flask import render_template, redirect, url_for, request, flash, session
from flask import jsonify
from app import app
from data.users import User
from data.plant import Plant
from data.users import User
from data.users import User
from data import db_session
from query_bd import get_plant_by_id, get_popular_plants
from sessions import get_count_plants

@app.route('/')
def home():
    # session['cart'] = {} #### TODO
    db_sess = db_session.create_session()
    products = get_popular_plants(db_sess)
    return render_template('index.html', products=products, session=session, count=get_count_plants(session['cart']) if 'cart' in session else 0)


@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    product_id = request.json.get('product_id')

    # Инициализируем корзину, если её нет
    if 'cart' not in session:
        session['cart'] = {}

    cart = session['cart']

    # Если товар уже в корзине, увеличиваем его количество
    if product_id in cart:
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

# Маршрут для показа карточки товара
@app.route('/plant/<int:plant_id>')
def created_cart_for_plant(plant_id):
    db_sess = db_session.create_session()
    plant = get_plant_by_id(db_sess, plant_id)  # Загрузка растенияы из БД
    return render_template('card_plant.html', plant=plant, count=get_count_plants(session['cart']))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Логика регистрации
        pass
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Логика авторизации
        pass
    return render_template('login.html')

@app.route('/cart')
def cart():
    # Логика корзины
    pass

@app.route('/admin')
def admin_dashboard():
    # Логика для админа
    pass

@app.route('/seller')
def seller_dashboard():
    # Логика для продавца
    pass