from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Base

con = create_engine('sqlite:///db.sqlite3')

Session = sessionmaker(bind=con, autocommit=True)  # autocommit - опасно
session = Session()

Base.metadata.create_all(con)


def get_model_by_tablename(tablename):  # получить модель по имени таблицы
    for model in Base._decl_class_registry.values():
        if hasattr(model, '__tablename__') and model.__tablename__ == tablename:
            return model


def get_columns(model):  # получить столбцы таблицы(модели)
    return model.__table__.columns.keys()
