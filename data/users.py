import sqlalchemy as sa
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


class User(SqlAlchemyBase):
    __tablename__ = 'users'
    
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    login = sa.Column(sa.String(50), nullable=False, unique=True)
    password = sa.Column(sa.String(255), nullable=False)
    email = sa.Column(sa.String(100), nullable=False)
    phone = sa.Column(sa.String(50), nullable=False)
    gender = sa.Column(sa.Enum('Male', 'Female', 'Other'), nullable=False)
    last_name = sa.Column(sa.String(100), nullable=False)
    first_name = sa.Column(sa.String(100), nullable=False)
    middle_name = sa.Column(sa.String(100), nullable=True)
    birth_date = sa.Column(sa.Date, nullable=True)
    user_type = sa.Column(sa.Enum('admin', 'user', 'seller', ' supplier'), nullable=False, default='user')
    registration_date = sa.Column(sa.TIMESTAMP, default=sa.func.current_timestamp())

    admins = orm.relationship("Admin", back_populates='user')
    supplier = orm.relationship("Supplier", back_populates='user')
    seller = orm.relationship("Seller", back_populates='user')
    order = orm.relationship("Order", back_populates='user')
    client = orm.relationship("Client", back_populates='user')