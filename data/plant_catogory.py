import sqlalchemy as sa
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


class PlantCategory(SqlAlchemyBase):
    __tablename__ = 'plant_categories'
    
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    name = sa.Column(sa.String(100), nullable=False)

    plant = orm.relationship("Plant", back_populates='category')

    def __str__(self):
        return self.name 
    
    def __repr__(self):
        return self.name