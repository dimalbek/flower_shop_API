from sqlalchemy import Column, Integer, String, Float, LargeBinary

from .database import Base


class Flower(Base):
    __tablename__ = "flowers"

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    name = Column(String, nullable=False)
    count = Column(Integer, nullable=True, default=1)
    cost = Column(Float, nullable=False)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, autoincrement=True, index=True)
    email = Column(String, unique=True, primary_key=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    password = Column(LargeBinary, nullable=False)
