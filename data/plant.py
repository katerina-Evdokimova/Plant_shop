import sqlalchemy as sa
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


class Plant(SqlAlchemyBase):
    __tablename__ = 'plants'
    
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    name = sa.Column(sa.String(100), nullable=False)
    category_id = sa.Column(sa.Integer, sa.ForeignKey('plant_categories.id'))
    description = sa.Column(sa.String(200), nullable=False)
    price = sa.Column(sa.Float)
    sale = sa.Column(sa.Integer, default=0)
    quantity = sa.Column(sa.Integer, default=0)
    picture = sa.Column(sa.String(200), nullable=False)

    items = orm.relationship("OrderItem", back_populates='plant')
    
    category = orm.relationship('PlantCategory')

    def __str__(self):
        return self.name 
    
    def __repr__(self):
        return self.name
