from flask import render_template, request, session, jsonify
from app import app
from login_manager import *
from query_bd import *
from flask import abort
from api import *

@app.route('/admin')
@login_required
def admin_dashboard():
    print(current_user)
    db_sess = db_session.create_session()
    if not is_admin(db_sess, current_user.id):  # Проверка наличия объекта Admin у пользователя
        abort(403)  # Ошибка доступа "403 Forbidden", если пользователь не администратор
    return render_template('panel_for_admins.html', current_user=current_user, admin=True, title='admin')
    

@app.route('/admin/table')
@login_required
def table_view():
    # Передаем данные для таблицы
    name_table = request.args.get('name', '')
    db_sess = db_session.create_session()
    if is_admin(db_sess, current_user.id) or is_seller(db_sess, current_user.id) and name_table == 'orders' \
            or is_supplier(db_sess, current_user.id) and name_table == 'plants':
        title, table_data = get_table_data_by_type(db_sess, name_table)

        print(table_data)
        # Параметры пагинации
        page = int(request.args.get('page', 1))  # текущая страница
        per_page = 10  # количество записей на странице
        total_pages = (len(table_data) + per_page - 1) // per_page

        # Обработка данных для отображения на текущей странице
        start = (page - 1) * per_page
        end = start + per_page
        table_page = table_data[start:end]

        print(table_data[0])
        return render_template('table.html', name_table=name_table, title=title, table=table_page, page=page, total_pages=total_pages, admin=is_admin(db_sess, current_user.id))
    
    return redirect('login')