from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String


Base = declarative_base()


class InitialTest(Base):
    __tablename__ = "initial_test"
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    description = Column(String(255))