import sqlalchemy as sa
from sqlalchemy import orm
from .db_session import SqlAlchemyBase

class Order(SqlAlchemyBase):
    __tablename__ = 'orders'
    
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    client_id = sa.Column(sa.Integer, sa.ForeignKey('clients.id'))
    status = sa.Column(sa.String(100), default="обработка")
    payment_method = sa.Column(sa.String(100))
    address = sa.Column(sa.String(100))
    
    client = orm.relationship('Client')
    items = orm.relationship('OrderItem', back_populates='order')