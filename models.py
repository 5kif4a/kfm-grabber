from sqlalchemy import Column, BIGINT, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()  # Декларативный стиль


class Person(Base):
    __tablename__ = 'Persons'

    index = Column(BIGINT, primary_key=True)
    lname = Column(Text)
    fname = Column(Text)
    mname = Column(Text)
    birthdate = Column(Text)  # Date
    iin = Column(Text)
    note = Column(Text)
    correction = Column(Text)
    category = Column(Text)


class Organization(Base):
    __tablename__ = 'Organizations'

    index = Column(BIGINT, primary_key=True)
    org_name = Column(Text)
    org_name_en = Column(Text)
    note = Column(Text)
    category = Column(Text)
