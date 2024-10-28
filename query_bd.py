from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import NoResultFound
from data.plant import Plant

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
    
from sqlalchemy import func
from data.order_items import OrderItem 

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