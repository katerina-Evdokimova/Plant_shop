from sqlalchemy.orm import Session, joinedload
from sqlalchemy import case, asc, desc
from sqlalchemy.exc import NoResultFound
from data.plant import Plant
from sqlalchemy import func
from data.order_items import OrderItem 

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