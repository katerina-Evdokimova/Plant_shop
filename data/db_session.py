import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base

SqlAlchemyBase = declarative_base()

__factory = None

def global_init(db_url):
    global __factory

    if __factory:
        return

    engine = sa.create_engine(db_url, echo=False)
    __factory = sessionmaker(bind=engine)

    from . import __all_models
    
    SqlAlchemyBase.metadata.create_all(engine)

def create_session() -> Session:
    global __factory
    return __factory()