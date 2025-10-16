from datetime import datetime, date
from sqlalchemy import Column, Integer, String, DateTime, Date, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from .db import Base

class Store(Base):
    __tablename__ = "stores"
    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False, unique=True)
    meta_visitas = Column(Integer, default=10)  # alterado para 10

    users = relationship("User", back_populates="store")
    clients = relationship("Client", back_populates="store")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False)
    email = Column(String(120), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="ATENDENTE")  # ADMIN/GERENTE/ATENDENTE
    lock_loja = Column(Boolean, default=True)  # True = vê só a loja; False = vê todas
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=True)  # None = todas (quando lock_loja=False)

    store = relationship("Store", back_populates="users")

class Client(Base):
    __tablename__ = "clients"
    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False)
    cpf = Column(String(20), nullable=True, unique=True)
    phone = Column(String(30), nullable=True)
    email = Column(String(255), nullable=True)
    birthday = Column(Date, nullable=True)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    store = relationship("Store", back_populates="clients")
    visits = relationship("Visit", back_populates="client")
    redemptions = relationship("Redemption", back_populates="client")

class Visit(Base):
    __tablename__ = "visits"
    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    client = relationship("Client", back_populates="visits")

class Redemption(Base):
    __tablename__ = "redemptions"
    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False)
    gift_name = Column(String(120), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    client = relationship("Client", back_populates="redemptions")
