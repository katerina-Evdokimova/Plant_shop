import sqlalchemy as sa
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


class Client(SqlAlchemyBase):
    __tablename__ = 'clients'
    
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'))  # Связь с таблицей User
    phone = sa.Column(sa.String(50), nullable=False)
    
    # Связь с таблицей пользователей
    user = orm.relationship('User')
    
    # Связь с таблицей адресов (один ко многим)
    addresses = orm.relationship('Address', back_populates='client', cascade='all, delete-orphan')
    order = orm.relationship("Order", back_populates='client')
