from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from .db import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String(120))
    email = Column(String(120), unique=True, index=True)
    password_hash = Column(String(255))
    role = Column(String(50), default="USER")
    lock_loja = Column(Boolean, default=False)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=True)

class Store(Base):
    __tablename__ = "stores"
    id = Column(Integer, primary_key=True)
    name = Column(String(120), unique=True)
    meta_visitas = Column(Integer, default=10)

class Client(Base):
    __tablename__ = "clients"
    id = Column(Integer, primary_key=True)
    name = Column(String(120))
    cpf = Column(String(14), unique=True, index=True)
    phone = Column(String(20))
    email = Column(String(120))
    birthday = Column(String(20))
    store_id = Column(Integer, ForeignKey("stores.id"))

class Visit(Base):
    __tablename__ = "visits"
    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey("clients.id"))
    store_id = Column(Integer, ForeignKey("stores.id"))
    created_at = Column(DateTime, default=func.now())

class Redemption(Base):
    __tablename__ = "redemptions"
    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey("clients.id"))
    store_id = Column(Integer, ForeignKey("stores.id"))
    gift_name = Column(String(120))
    created_at = Column(DateTime, default=func.now())
