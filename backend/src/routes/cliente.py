from __future__ import annotations

from datetime import date, datetime
from typing import Any, Dict, Optional

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from ..db import SessionLocal
from ..models import Client

cliente_bp = Blueprint("cliente", __name__)


def _parse_birthday(value: Optional[str | date]) -> Optional[date]:
    """Aceita 'YYYY-MM-DD' ou 'DD/MM/YYYY' (ou None) e devolve date."""
    if value in (None, "", "null"):
        return None
    if isinstance(value, date):
        return value
    s = str(value).strip()
    # ISO primeiro
    try:
        return date.fromisoformat(s)
    except Exception:
        pass
    # BR dd/mm/yyyy
    try:
        return datetime.strptime(s, "%d/%m/%Y").date()
    except Exception:
        return None


def _client_to_dict(c: Client) -> Dict[str, Any]:
    return {
        "id": c.id,
        "name": c.name,
        "cpf": c.cpf,
        "phone": c.phone,
        "email": c.email,
        # sempre em ISO no JSON
        "birthday": c.birthday.isoformat() if c.birthday else None,
        "store_id": c.store_id,
        "created_at": c.created_at.isoformat() if c.created_at else None,
    }


@cliente_bp.post("/api/clientes")
@jwt_required()
def create_client():
    data = request.get_json(silent=True) or {}
    with SessionLocal() as db:
        client = Client(
            name=data.get("name"),
            cpf=data.get("cpf"),
            phone=data.get("phone"),
            email=data.get("email"),
            birthday=_parse_birthday(data.get("birthday")),
            store_id=data.get("store_id"),
        )
        db.add(client)
        db.commit()
        db.refresh(client)
        return jsonify(_client_to_dict(client)), 201


@cliente_bp.get("/api/clientes")
@jwt_required()
def list_clients():
    with SessionLocal() as db:
        rows = db.query(Client).order_by(Client.id.desc()).limit(100).all()
        return jsonify([_client_to_dict(c) for c in rows])
