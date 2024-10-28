import sqlalchemy as sa
from sqlalchemy import orm
from data.db_session import SqlAlchemyBase

class Admin(SqlAlchemyBase):
    __tablename__ = 'admins'
    
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'))

    user = orm.relationship('User')