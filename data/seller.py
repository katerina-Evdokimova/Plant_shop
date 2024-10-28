import sqlalchemy as sa
from sqlalchemy import orm
from data.db_session import SqlAlchemyBase

class Seller(SqlAlchemyBase):
    __tablename__ = 'sellers'
    
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'))
    phone = sa.Column(sa.String(50), nullable=False)

    user = orm.relationship('User')