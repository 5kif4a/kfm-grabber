from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()  # Декларативный стиль


class Person:
    id = Column(Integer, primary_key=True)
    lname = Column(String)
    fname = Column(String)
    mname = Column(String)
    birthdate = Column(Date)
    iin = Column(String)
    note = Column(String)
    correction = Column(String)
    category = Column(String)


class Organization:
    num = Column(Integer, primary_key=True)
    org_name = Column(String)
    org_name_en = Column(String)
    note = Column(String)
    category = Column(String)






