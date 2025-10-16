from __future__ import annotations

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import relationship

from .db import Base


# ============= STORES =============
class Store(Base):
    __tablename__ = "stores"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    meta_visitas = Column(Integer, nullable=False, default=10)
    created_at = Column(DateTime, server_default=func.now())

    # relacionamentos (opcionais)
    users = relationship("User", back_populates="store", lazy="selectin")
    clients = relationship("Client", back_populates="store", lazy="selectin")
    visits = relationship("Visit", back_populates="store", lazy="selectin")
    redemptions = relationship("Redemption", back_populates="store", lazy="selectin")

    def __repr__(self) -> str:
        return f"<Store id={self.id} name={self.name!r} meta={self.meta_visitas}>"


# ============== USERS =============
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False, default="ATENDENTE")  # ADMIN | GERENTE | ATENDENTE
    lock_loja = Column(Boolean, nullable=False, default=False)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    store = relationship("Store", back_populates="users", lazy="joined")

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email!r} role={self.role}>"


# ============= CLIENTS =============
class Client(Base):
    __tablename__ = "clients"
    __table_args__ = (
        UniqueConstraint("cpf", name="uq_clients_cpf"),
    )

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    cpf = Column(String, nullable=True)          # único (ver UniqueConstraint)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    birthday = Column(Date, nullable=True)       # <-- IMPORTANTE: Date (alinha com Postgres)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    store = relationship("Store", back_populates="clients", lazy="joined")
    visits = relationship("Visit", back_populates="client", lazy="selectin", cascade="all, delete-orphan")
    redemptions = relationship("Redemption", back_populates="client", lazy="selectin", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Client id={self.id} cpf={self.cpf!r} name={self.name!r}>"


# ============== VISITS =============
class Visit(Base):
    __tablename__ = "visits"

    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    client = relationship("Client", back_populates="visits", lazy="joined")
    store = relationship("Store", back_populates="visits", lazy="joined")

    def __repr__(self) -> str:
        return f"<Visit id={self.id} client_id={self.client_id}>"


# ============ REDEMPTIONS ============
class Redemption(Base):
    __tablename__ = "redemptions"

    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=True)
    gift_name = Column(String, nullable=False, default="1 Kg de Vela Palito")
    created_at = Column(DateTime, server_default=func.now())

    client = relationship("Client", back_populates="redemptions", lazy="joined")
    store = relationship("Store", back_populates="redemptions", lazy="joined")

    def __repr__(self) -> str:
        return f"<Redemption id={self.id} client_id={self.client_id} gift={self.gift_name!r}>"
