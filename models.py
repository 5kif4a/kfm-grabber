from sqlalchemy import Column, BIGINT, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()  # Декларативный стиль


def get_model_by_tablename(tablename): # получить модель по имени таблицы
    for model in Base._decl_class_registry.values():
        if hasattr(model, '__tablename__') and model.__tablename__ == tablename:
            return model


class Person(Base):
    __tablename__ = 'persons'

    index = Column(BIGINT, primary_key=True, index=True)
    lname = Column(Text)
    fname = Column(Text)
    mname = Column(Text)
    birthdate = Column(Text)  # Date
    iin = Column(Text)
    note = Column(Text)
    correction = Column(Text)
    status = Column(Text)

    def __repr__(self):
        return '<Person({},{},{},{},{},{},{},{})>'.format(self.lname, self.fname, self.mname,
                                                          self.birthdate, self.iin, self.note, self.correction,
                                                          self.status)


class Organization(Base):
    __tablename__ = 'organizations'

    index = Column(BIGINT, primary_key=True, index=True)
    org_name = Column(Text)
    org_name_en = Column(Text)
    note = Column(Text)
    status = Column(Text)

    def __repr__(self):
        return '<Organization({},{},{},{},{))>'.format(self.index, self.org_name, self.org_name_en,
                                                       self.note, self.status)
