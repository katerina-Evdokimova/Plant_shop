from flask import render_template, request, session
from flask import jsonify
from app import app
from sessions import get_count_plants
from query_bd import get_plant_by_id, get_plants
from routes_main_page import *


@app.route('/reload', methods=['POST'])
def reload():
    return jsonify(count=get_count_plants(session['cart'] if 'cart' in session else {}))


@app.route('/trash')
def trash():
    db_sess = db_session.create_session()
    plants = [get_plant_by_id(db_sess, idx) for idx in session['cart'].keys()] if 'cart' in session else []
    return render_template('trash.html', plants=plants, session=session)

@app.route('/catalog')
def catalog():
    # Получаем параметр сортировки из URL
    sort_order = request.args.get('sort', '')  # По умолчанию сортировка 'asc' (возрастание)
    # Открываем сессию базы данных
    db_sess = db_session.create_session()

    # Передаем параметр сортировки в функцию get_plants
    plants = get_plants(db_sess, sort_order)
    db_sess = db_session.create_session()
    plants = get_plants(db_sess)
    return render_template('catalog.html', products=plants, session=session, n=12)


@app.route('/catalog/sort', methods=['POST'])
def catalog_sort():  
    sort_order = request.args.get('sort', 'asc')
    n = int(request.json.get('n'))
    db_sess = db_session.create_session()
    plants = get_plants(db_sess, sort_order)
    session['sort'] = sort_order
    return jsonify({'templates': render_template(
        'cart_section.html', products=plants, session=session, n=n), 
        "has_more": len(plants) <= 12})


@app.route('/load-more-products', methods=['POST'])
def load_more_products():
    n = int(request.json.get('n'))
    db_sess = db_session.create_session()
    if 'sort' in session:
        plants = get_plants(db_sess, session['sort'])[n:]
    else:
        plants = get_plants(db_sess)[n:]
    return jsonify({'templates': render_template(
        'cart_section.html', products=plants, session=session, n=n), 
        "has_more": len(plants) <= 12})

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