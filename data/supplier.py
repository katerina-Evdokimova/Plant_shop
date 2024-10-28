import sqlalchemy as sa
from sqlalchemy import orm
from .db_session import SqlAlchemyBase

class Supplier(SqlAlchemyBase):
    __tablename__ = 'suppliers'
    
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'))
    name = sa.Column(sa.String(100), nullable=False)
    contact = sa.Column(sa.String(100), nullable=False)

    user = orm.relationship('User')