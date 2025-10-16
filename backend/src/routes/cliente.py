from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy import select
from ..db import SessionLocal
from ..models import Client

cliente_bp = Blueprint("cliente_bp", __name__)

@cliente_bp.get("/clientes/cpf/<cpf>")
@jwt_required()
def get_cliente_por_cpf(cpf):
    cpf = (cpf or "").strip()
    db = SessionLocal()
    try:
        c = db.execute(select(Client).where(Client.cpf == cpf)).scalar_one_or_none()
        if not c:
            return jsonify({"error": "not found"}), 404
        return jsonify({"id": c.id, "name": c.name, "cpf": c.cpf, "phone": c.phone, "email": c.email})
    finally:
        db.close()

@cliente_bp.get("/clientes/buscar")
@jwt_required()
def buscar_cliente():
    cpf = (request.args.get("cpf") or "").strip()
    if not cpf:
        return jsonify({"error": "cpf obrigatório"}), 422
    db = SessionLocal()
    try:
        c = db.execute(select(Client).where(Client.cpf == cpf)).scalar_one_or_none()
        if not c:
            return jsonify({"error": "not found"}), 404
        return jsonify({"id": c.id, "name": c.name, "cpf": c.cpf, "phone": c.phone, "email": c.email})
    finally:
        db.close()
