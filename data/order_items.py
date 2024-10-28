import sqlalchemy as sa
from sqlalchemy import orm
from .db_session import SqlAlchemyBase

class OrderItem(SqlAlchemyBase):
    __tablename__ = 'order_items'
    
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    order_id = sa.Column(sa.Integer, sa.ForeignKey('orders.id'))
    plant_id = sa.Column(sa.Integer, sa.ForeignKey('plants.id'))
    quantity = sa.Column(sa.Integer)
    
    order = orm.relationship('Order', back_populates='items')
    plant = orm.relationship('Plant')