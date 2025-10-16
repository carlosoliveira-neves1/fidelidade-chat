from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    String,
    Integer,
    DateTime,
    ForeignKey,
    Boolean,
    Text,
    func,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


class Store(Base):
    __tablename__ = "stores"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    meta_visitas: Mapped[int] = mapped_column(Integer, nullable=False, default=10)

    users: Mapped[List["User"]] = relationship("User", back_populates="store")
    clients: Mapped[List["Client"]] = relationship("Client", back_populates="store")
    visits: Mapped[List["Visit"]] = relationship("Visit", back_populates="store")
    redemptions: Mapped[List["Redemption"]] = relationship(
        "Redemption", back_populates="store"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), server_default=func.now()
    )


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    # ADMIN, GERENTE, ATENDENTE
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="ATENDENTE")

    # se True, o usuário fica travado numa loja específica (store_id)
    lock_loja: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    store_id: Mapped[Optional[int]] = mapped_column(ForeignKey("stores.id"), nullable=True)

    store: Mapped[Optional["Store"]] = relationship("Store", back_populates="users")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), server_default=func.now()
    )


class Client(Base):
    __tablename__ = "clients"
    __table_args__ = (
        UniqueConstraint("cpf", name="uq_clients_cpf"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    cpf: Mapped[str] = mapped_column(String(14), nullable=False, index=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # IMPORTANTE: agora é string 'YYYY-MM-DD' para alinhar ao banco (VARCHAR(10))
    birthday: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)

    store_id: Mapped[Optional[int]] = mapped_column(ForeignKey("stores.id"), nullable=True)
    store: Mapped[Optional["Store"]] = relationship("Store", back_populates="clients")

    visits: Mapped[List["Visit"]] = relationship("Visit", back_populates="client")
    redemptions: Mapped[List["Redemption"]] = relationship(
        "Redemption", back_populates="client"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), server_default=func.now()
    )


class Visit(Base):
    __tablename__ = "visits"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"), nullable=False)
    store_id: Mapped[Optional[int]] = mapped_column(ForeignKey("stores.id"), nullable=True)

    client: Mapped["Client"] = relationship("Client", back_populates="visits")
    store: Mapped[Optional["Store"]] = relationship("Store", back_populates="visits")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), server_default=func.now()
    )


class Redemption(Base):
    __tablename__ = "redemptions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"), nullable=False)
    store_id: Mapped[Optional[int]] = mapped_column(ForeignKey("stores.id"), nullable=True)

    gift_name: Mapped[str] = mapped_column(String(255), nullable=False, default="Brinde")

    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    client: Mapped["Client"] = relationship("Client", back_populates="redemptions")
    store: Mapped[Optional["Store"]] = relationship("Store", back_populates="redemptions")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), server_default=func.now()
    )
