import sqlalchemy as sa
from sqlalchemy import orm
from .db_session import SqlAlchemyBase

class Order(SqlAlchemyBase):
    __tablename__ = 'orders'
    
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'))
    status = sa.Column(sa.String(100), default="pending")
    
    user = orm.relationship('User')
    items = orm.relationship('OrderItem', back_populates='order')