import sqlalchemy as sa
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


class Client(SqlAlchemyBase):
    __tablename__ = 'clients'
    
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'))  # Связь с таблицей User
    address = sa.Column(sa.String(100), nullable=False)
    phone = sa.Column(sa.String(50), nullable=False)

    user = orm.relationship('User')