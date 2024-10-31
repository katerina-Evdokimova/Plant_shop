import sqlalchemy as sa
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


class Address(SqlAlchemyBase):
    __tablename__ = 'address'
    
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    client_id = sa.Column(sa.Integer, sa.ForeignKey('clients.id'))  # Связь с таблицей Client
    address = sa.Column(sa.String(100), default="")
    
    # Связь с клиентом (обратное отношение)
    client = orm.relationship('Client', back_populates='addresses')

def __str__(self):
    return f'name: {self.name},\nprice: {self.price - (self.price * self.sale / 100)},\nsale: {self.sale}\n\n' 

def __repr__(self):
    return f'name: {self.name},\nprice: {self.price - (self.price * self.sale / 100)},\nsale: {self.sale}\n\n' 
 
