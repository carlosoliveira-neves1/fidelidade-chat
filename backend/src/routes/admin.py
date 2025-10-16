from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from sqlalchemy import select
from ..db import SessionLocal
from ..models import Store

admin_bp = Blueprint("admin_bp", __name__)

def _is_admin():
    claims = get_jwt() or {}
    return claims.get("role") == "ADMIN"

@admin_bp.post("/lojas")
@jwt_required()
def criar_loja():
    if not _is_admin():
        return jsonify({"error": "forbidden"}), 403
    data = request.get_json(force=True)
    name = (data.get("name") or "").strip()
    meta = int(data.get("meta_visitas") or 10)
    if not name:
        return jsonify({"error": "name obrigatório"}), 422
    db = SessionLocal()
    try:
        exists = db.execute(select(Store).where(Store.name == name)).scalar_one_or_none()
        if exists:
            return jsonify({"error": "loja já existe"}), 400
        s = Store(name=name, meta_visitas=meta)
        db.add(s)
        db.commit()
        return jsonify({"id": s.id, "name": s.name, "meta_visitas": s.meta_visitas}), 201
    finally:
        db.close()

@admin_bp.get("/lojas")
@jwt_required()
def listar_lojas():
    if not _is_admin():
        return jsonify({"error": "forbidden"}), 403
    db = SessionLocal()
    try:
        items = db.execute(select(Store).order_by(Store.id.asc())).scalars().all()
        return jsonify([{"id": x.id, "name": x.name, "meta_visitas": x.meta_visitas} for x in items])
    finally:
        db.close()
