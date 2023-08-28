from sqlalchemy import (Boolean, Column, DateTime, ForeignKey, Integer,
                        create_engine)
from sqlalchemy.orm import declarative_base, sessionmaker

engine = create_engine('sqlite:///test.db', future=True)

Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True)


class Company(Base):
    __tablename__ = 'company'

    id = Column(Integer, primary_key=True)
    inn = Column(Integer, unique=True)
    ogrn = Column(Integer, unique=True)
    is_sole_entrepreneur = Column(Boolean)


class Request(Base):
    __tablename__ = 'request'

    id = Column(Integer, primary_key=True)
    user = Column(ForeignKey('user.id'))
    company = Column(ForeignKey('company.id'))
    date = Column(DateTime)


Base.metadata.create_all(engine)
