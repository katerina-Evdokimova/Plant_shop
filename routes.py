from flask import render_template, request, session
from flask import jsonify
from app import app
from sessions import get_count_plants
from query_bd import get_plant_by_id
from routes_main_page import *


@app.route('/reload', methods=['POST'])
def reload():
    return jsonify(count=get_count_plants(session['cart'] if 'cart' in session else {}))


@app.route('/trash')
def trash():
    db_sess = db_session.create_session()
    plants = [get_plant_by_id(db_sess, idx) for idx in session['cart'].keys()] if 'cart' in session else []
    return render_template('trash.html', plants=plants, session=session)


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