from sqlalchemy import Column, BIGINT, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()  # Декларативный стиль


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
