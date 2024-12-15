from flask import render_template, request, session
from flask import jsonify
from sqlalchemy import and_
from app import app
from sessions import get_count_plants
from query_bd import get_plant_by_id, get_plants, get_client_by_id, get_address_by_id, delails_order_by_order_id
from query_bd import get_address_by_id, delails_order_by_order_id
from routes_main_page import *
from data.users import User
from data.plant import Plant
from data.client import Client
from data.admin import Admin
from data.order_items import OrderItem
from data.address import Address
from data.order import Order
from wtf_flask.login_form import LoginForm
from wtf_flask.register_form import RegistrationForm
from wtf_flask.edit_profile import ProfileForm
from login_manager import *
from routes_admin import *
from routes_error import *
from werkzeug.security import generate_password_hash, check_password_hash
from api import *

@app.route('/reload', methods=['POST'])
def reload():
    return jsonify(count=get_count_plants(session['cart'] if 'cart' in session else {}))


@app.route('/trash')
def trash():
    db_sess = db_session.create_session()
    plants = [get_plant_by_id(db_sess, idx) for idx in session['cart'].keys()] if 'cart' in session else []
    return render_template('trash.html', plants=plants, session=session, current_user=current_user, admin=False, title='Корзина')

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
    return render_template('catalog.html',current_user=current_user, products=plants, session=session, n=12, title='Каталог')


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
    print('cccccc')
    db_sess = db_session.create_session()
    print(request.method)
    if not get_client_by_id(db_sess, current_user.id):
        new_client = Client(user_id=current_user.id, phone=current_user.phone)
        db_sess.add(new_client)
        db_sess.commit()
    
    # Если пользователь авторизован, показываем страницу оформления заказа
    if request.method == 'POST':
        print('dddd')
        # Получаем данные из формы
        name = request.form.get('name')
        phone = request.form.get('phone')
        payment_method = request.form.get('payment_method')
        selected_address = request.form.get('address')
        new_address = request.form.get('new_address')
        print('Ваш заказ not not успешно оформлен!', selected_address)
        client_id = get_client_by_id(db_sess, current_user.id).id
        # Проверка, был ли выбран новый адрес
        if selected_address == 'new':
            if not new_address:
                flash('Введите новый адрес доставки.')
                return redirect(url_for('checkout'))
            address = new_address
            # Сохраняем новый адрес в базу данных для пользователя
            if not db_sess.query(Address).filter(and_(Address.client_id == client_id,
                                                 Address.address == address)).first():
                
                new_address_entry = Address(client_id=client_id, address=new_address)
                db_sess.add(new_address_entry)
                db_sess.commit()
        else:
            # Используем выбранный адрес из выпадающего списка
            address = selected_address
        print('aaaaaaaaaaâ')
        
        # Проверяем, есть ли товары в корзине
        if 'cart' not in session or not session['cart']:
            flash('Ваша корзина пуста!')
            return redirect(url_for('catalog'))  # Перенаправляем на каталог

        print(address)
        # Создаем запись о новом заказе
        new_order = Order(client_id=client_id, address=address, payment_method=payment_method)
        db_sess.add(new_order)
        db_sess.commit()  # Сначала сохраняем заказ, чтобы получить его ID
        print('Ваш заказ not успешно оформлен!')

        # Обрабатываем товары в корзине
        cart = session['cart']
        total_sum = 0
        for plant_id, quantity in cart.items():
            plant = db_sess.query(Plant).get(plant_id)
            if plant:
                if plant.quantity >= quantity:
                    # Уменьшаем количество
                    plant.quantity -= quantity
                else:
                    flash(f'Недостаточно {plant.name} на складе')
                    return redirect(url_for('cart'))
            
                item_total = plant.price * quantity
                total_sum += item_total

                # Создаем запись о каждом товаре в заказе
                order_item = OrderItem(order_id=new_order.id, plant_id=plant.id, quantity=quantity, price=item_total)
                db_sess.add(order_item)

        # Сохраняем общую сумму заказа
        new_order.total_sum = total_sum
        db_sess.commit()

        # Очищаем корзину после успешного заказа
        session.pop('cart', {})
        flash('Ваш заказ успешно оформлен!')
        return redirect(url_for('order_confirmation', order_id=new_order.id))
         

    print(current_user)
    client_id = get_client_by_id(db_sess, current_user.id).id
    adress = [el.address for el in get_address_by_id(db_sess, client_id)]
    adress = adress if adress else []
    print(adress)
    plants = [get_plant_by_id(db_sess, idx) for idx in session['cart'].keys()] if 'cart' in session else []
    total_sum = sum([session['cart'][str(plant.id)] * plant.price * (1 - plant.sale / 100) for plant in plants])
    all_aum = sum([session['cart'][str(plant.id)] * plant.price for plant in plants])
    return render_template('checkout.html', current_user=current_user, user_addresses=adress, plants=plants, total_sum=total_sum, all_sum=all_aum, admin=False, title='Оформление')  # Отображение формы для оформления заказа



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
    
    return render_template('register.html', form=form, title='Регистрация')


@app.route('/order_confirmation')
@login_required
def order_confirmation():
    order_id = request.args.get('order_id')
    # Получаем заказ текущего пользователя
    db_sess = db_session.create_session()
    order = db_sess.query(Order).filter(Order.id == order_id).first()
    order_item = delails_order_by_order_id(db_sess, order.id)
    print(order_item)
    total_amount = sum(item['price'] for item in order_item)
    return render_template('order_details.html', order=order, order_items=order_item, total_amount=total_amount, admin=False, title='Оформление заказа')


@app.route('/orders')
@login_required
def my_orders():
    # Получаем заказы текущего пользователя
    db_sess = db_session.create_session()
    client = db_sess.query(Client).filter(Client.user_id == current_user.id).first()
    orders = db_sess.query(Order).filter(Order.client_id == client.id).all()
    print(orders, current_user.id)
    total_amount = {}
    for order in orders:
        order_item = delails_order_by_order_id(db_sess, order.id)
        total_amount[order.id] =  sum(item['price'] for item in order_item)
        
    return render_template('orders.html', orders=orders, total_amount=total_amount, admin=False, title='Заказы')


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
            return redirect(next_page or url_for('catalog'))  # Перенаправление на страницу оформления заказа
        else:
            flash('Неверный логин или пароль', 'danger')
    
    return render_template('login.html', form=form, admin=False, title='Логин')

@app.route('/account', methods=['GET', 'POST'])
@login_required
def edit_profile():
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == current_user.id).first()
    
    # Передаем данные пользователя в форму
    form = ProfileForm(obj=user)

    if request.method == 'POST' and form.validate_on_submit():
        changes = []

        # Сравниваем и обновляем только измененные поля
        if user.login != form.login.data:
            user.login = form.login.data
            changes.append("логин")
        if user.email != form.email.data:
            user.email = form.email.data
            changes.append("email")
        if user.phone != form.phone.data:
            user.phone = form.phone.data
            changes.append("телефон")
        if user.gender != form.gender.data:
            user.gender = form.gender.data
            changes.append("пол")
        if user.first_name != form.first_name.data:
            user.first_name = form.first_name.data
            changes.append("имя")
        if user.last_name != form.last_name.data:
            user.last_name = form.last_name.data
            changes.append("фамилия")
        if user.middle_name != form.middle_name.data:
            user.middle_name = form.middle_name.data
            changes.append("отчество")

        # Проверяем изменение пароля
        if form.new_password.data:
            user.password = generate_password_hash(form.new_password.data)
            changes.append("пароль")

        # Сохраняем изменения
        db_sess.commit()
        flash(f"Обновлены поля: {', '.join(changes)}", "success")
        return redirect('/account')

    return render_template('profile.html', form=form)
    

@app.route('/seller')
@login_required
def seller_dashboard():
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == current_user.id).first()
    client_id = get_client_by_id(db_sess, current_user.id).id
    adress = [el for el in get_address_by_id(db_sess, client_id)]
    adress = adress if adress else []
    print(adress)

    return render_template('profile.html', users=user, addresses=adress, admin=False, title='Аккаунт')

