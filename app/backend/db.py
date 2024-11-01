from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, DeclarativeBase

engine = create_engine('sqlite:///taskmanager.db')

Session_local = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass

