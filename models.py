from sqlalchemy import (
    Column, Integer, Boolean, Text, Numeric, ForeignKey, DateTime, String, Date
)
from sqlalchemy.orm import relationship

from database import Base


class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(25), unique=True, nullable=False)
    name = Column(String(50))
    email = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_staff = Column(Boolean, default=False)


    currency = Column(String(10), default="UZS")

    persons = relationship("Person", back_populates="user", cascade="all, delete-orphan")
    debts = relationship("Debt", back_populates="user", cascade="all, delete-orphan")


class Person(Base):
    __tablename__ = 'persons'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    full_name = Column(String(150), nullable=False)

    user = relationship("Users", back_populates="persons")
    debts = relationship("Debt", back_populates="person", cascade="all, delete-orphan")


class Debt(Base):
    __tablename__ = 'debt'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    person_id = Column(Integer, ForeignKey("persons.id"), nullable=False)
    debt_type = Column(String(20), nullable=False)
    summa = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(10), nullable=False)
    description = Column(Text)
    date_get = Column(Date)
    date_give = Column(Date)
    reminder_at = Column(Date)

    user = relationship("Users", back_populates="debts")
    person = relationship("Person", back_populates="debts")

    @property
    def person_full_name(self):
        return self.person.full_name