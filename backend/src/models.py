# src/models.py
from __future__ import annotations

from datetime import datetime, date
from typing import List, Optional

from sqlalchemy import (
    String,
    Integer,
    Boolean,
    DateTime,
    Date,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


# =========================
# STORES
# =========================
class Store(Base):
    __tablename__ = "stores"
    __table_args__ = (UniqueConstraint("name", name="uq_stores_name"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(120))
    meta_visitas: Mapped[int] = mapped_column(Integer, nullable=False, default=10)

    # backrefs
    users: Mapped[List["User"]] = relationship(back_populates="store")
    clients: Mapped[List["Client"]] = relationship(back_populates="store")
    visits: Mapped[List["Visit"]] = relationship(back_populates="store")
    redemptions: Mapped[List["Redemption"]] = relationship(back_populates="store")

    def __repr__(self) -> str:
        return f"<Store id={self.id} name={self.name!r} meta={self.meta_visitas}>"


# =========================
# USERS
# =========================
class User(Base):
    __tablename__ = "users"
    __table_args__ = (UniqueConstraint("email", name="uq_users_email"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(255))
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20), default="ATENDENTE")  # ADMIN | GERENTE | ATENDENTE
    lock_loja: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    store_id: Mapped[Optional[int]] = mapped_column(ForeignKey("stores.id"), nullable=True)
    store: Mapped[Optional[Store]] = relationship(back_populates="users")

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email!r} role={self.role}>"


# =========================
# CLIENTS
# =========================
class Client(Base):
    __tablename__ = "clients"
    __table_args__ = (UniqueConstraint("cpf", name="uq_clients_cpf"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(120))
    cpf: Mapped[str] = mapped_column(String(14))  # apenas dígitos na prática
    phone: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # >>> AJUSTE IMPORTANTE: Date, não String
    birthday: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    store_id: Mapped[Optional[int]] = mapped_column(ForeignKey("stores.id"), nullable=True)
    store: Mapped[Optional[Store]] = relationship(back_populates="clients")

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    visits: Mapped[List["Visit"]] = relationship(back_populates="client")
    redemptions: Mapped[List["Redemption"]] = relationship(back_populates="client")

    def __repr__(self) -> str:
        return f"<Client id={self.id} cpf={self.cpf!r} name={self.name!r}>"


# =========================
# VISITS (registros de visita)
# =========================
class Visit(Base):
    __tablename__ = "visits"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"), nullable=False)
    client: Mapped[Client] = relationship(back_populates="visits")

    store_id: Mapped[Optional[int]] = mapped_column(ForeignKey("stores.id"), nullable=True)
    store: Mapped[Optional[Store]] = relationship(back_populates="visits")

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    def __repr__(self) -> str:
        return f"<Visit id={self.id} client_id={self.client_id} store_id={self.store_id}>"


# =========================
# REDEMPTIONS (resgates)
# =========================
class Redemption(Base):
    __tablename__ = "redemptions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"), nullable=False)
    client: Mapped[Client] = relationship(back_populates="redemptions")

    store_id: Mapped[Optional[int]] = mapped_column(ForeignKey("stores.id"), nullable=True)
    store: Mapped[Optional[Store]] = relationship(back_populates="redemptions")

    gift_name: Mapped[str] = mapped_column(String(120), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    def __repr__(self) -> str:
        return f"<Redemption id={self.id} client_id={self.client_id} gift={self.gift_name!r}>"
