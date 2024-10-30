from flask import render_template, request, session
from flask import jsonify
from app import app
from sessions import get_count_plants
from query_bd import get_plant_by_id, get_plants
from routes_main_page import *
from data.users import User
from wtf_flask.login_form import LoginForm
from wtf_flask.register_form import RegistrationForm
from login_manager import *
from werkzeug.security import generate_password_hash, check_password_hash


@app.route('/reload', methods=['POST'])
def reload():
    return jsonify(count=get_count_plants(session['cart'] if 'cart' in session else {}))


@app.route('/trash')
def trash():
    db_sess = db_session.create_session()
    plants = [get_plant_by_id(db_sess, idx) for idx in session['cart'].keys()] if 'cart' in session else []
    return render_template('trash.html', plants=plants, session=session, current_user=current_user)

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
    return render_template('catalog.html',current_user=current_user, products=plants, session=session, n=12)


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


@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    # Если пользователь авторизован, показываем страницу оформления заказа
    if request.method == 'POST':
        # Обработка заказа
        # Логика по созданию заказа и записи в БД
        return redirect(url_for('order_confirmation'))
    
    return render_template('checkout.html')  # Отображение формы для оформления заказа

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # Создаем нового пользователя с зашифрованным паролем
        hashed_password = generate_password_hash(form.password.data)
        
        # Открываем сессию для записи данных в БД
        db_sess = db_session.create_session()
        
        # Создаем нового пользователя
        user = User(
            login=form.login.data,
            email=form.email.data,
            phone=form.phone.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            middle_name=form.middle_name.data,
            birth_date=form.birth_date.data,
            gender=form.gender.data,
            password=hashed_password
        )
        
        db_sess.add(user)
        db_sess.commit()
        next_page = request.args.get('next')

        flash('Регистрация прошла успешно!', 'success')
        return redirect(next_page or url_for('login'))
    
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()  # Создание сессии для работы с БД
        user = db_sess.query(User).filter(User.login == form.login.data).first()
        next_page = request.args.get('next')
        # Проверка, существует ли пользователь и совпадает ли пароль
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)  # Авторизация пользователя
            return redirect(next_page or url_for(''))  # Перенаправление на страницу оформления заказа
        else:
            flash('Неверный логин или пароль', 'danger')
    
    return render_template('login.html', form=form)

@app.route('/account')
def account():
    if current_user.is_authenticated:
        # Логика для авторизованных пользователей
        pass
    else:
        return redirect(url_for('login'))
    

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