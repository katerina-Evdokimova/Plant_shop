from flask import render_template, request, session, jsonify
from app import app
from login_manager import *
from query_bd import is_admin
from flask import abort
from admin_dashboards import *



@app.route('/admin')
@login_required
def admin_dashboard():
    print(current_user)
    db_sess = db_session.create_session()
    if not is_admin(db_sess, current_user.id):  # Проверка наличия объекта Admin у пользователя
        abort(403)  # Ошибка доступа "403 Forbidden", если пользователь не администратор
    return render_template('panel_for_admins.html', current_user=current_user, admin=True)
    

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

@app.route('/api/top_products')
def top_products():
    return jsonify(get_top_products())