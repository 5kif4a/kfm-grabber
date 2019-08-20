from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base

# read URL for connection to database from config file
with open('config', 'r', encoding='utf8') as f:
    args = [row for row in f.read().split('\n')]


url = 'postgresql://{}:{}@{}:{}/{}'.format(*args)
con = create_engine(url, client_encoding='utf8', echo=False)

Session = sessionmaker(bind=con, autocommit=True)  # autocommit - опасно
session = Session()


def get_model_by_tablename(tablename):  # получить модель по имени таблицы
    for model in Base._decl_class_registry.values():
        if hasattr(model, '__tablename__') and model.__tablename__ == tablename:
            return model


def get_columns(model):  # получить столбцы таблицы(модели)
    return model.__table__.columns.keys()
