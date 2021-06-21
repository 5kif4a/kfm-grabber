import datetime as dt

from sqlalchemy import Column, BIGINT, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()  # Декларативный стиль


class Person(Base):
    __tablename__ = 'persons'

    index = Column(BIGINT, primary_key=True)
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

    index = Column(BIGINT, primary_key=True)
    org_name = Column(Text)
    org_name_en = Column(Text)
    note = Column(Text)
    status = Column(Text)

    def __repr__(self):
        return '<Organization({},{},{},{},{))>'.format(self.index, self.org_name, self.org_name_en,
                                                       self.note, self.status)


class History(Base):
    __tablename__ = 'history'

    index = Column(BIGINT, primary_key=True, index=True)
    table = Column(Text)
    obj_id = Column(BIGINT)
    note = Column(Text)
    date = Column(Text, default=dt.datetime.now().strftime('%d.%m.%Y %H:%M'))

    def __repr__(self):
        return '<History({},{},{},{},{))>'.format(self.index, self.table, self.obj_id,
                                                  self.note, self.date)
