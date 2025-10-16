from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy import select, func, desc
from ..db import SessionLocal
from ..models import Client, Visit, Store

visita_bp = Blueprint("visita_bp", __name__)

@visita_bp.post("/visitas")
@jwt_required()
def registrar_visita():
    data = request.get_json(force=True)
    cpf = (data.get("cpf") or "").strip()
    client_id = data.get("client_id")
    db = SessionLocal()
    try:
        c = None
        if cpf:
            c = db.execute(select(Client).where(Client.cpf == cpf)).scalar_one_or_none()
        elif client_id:
            c = db.get(Client, int(client_id))
        if not c:
            return jsonify({"error": "Cliente não encontrado"}), 404
        store_id = c.store_id or 1
        v = Visit(client_id=c.id, store_id=store_id)
        db.add(v)
        db.commit()
        count = db.execute(select(func.count(Visit.id)).where(Visit.client_id == c.id)).scalar_one()
        return jsonify({"visit_id": v.id, "visits_count": int(count)}), 201
    finally:
        db.close()

@visita_bp.get("/visitas")
@jwt_required()
def listar_visitas():
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 10))
    db = SessionLocal()
    try:
        q = select(Visit).order_by(desc(Visit.created_at))
        total = db.execute(select(func.count()).select_from(q.subquery())).scalar_one()
        items = db.execute(q.offset((page-1)*per_page).limit(per_page)).scalars().all()
        return jsonify({"total": int(total), "items": [{"id": v.id, "client_id": v.client_id, "store_id": v.store_id, "created_at": v.created_at.isoformat()} for v in items]})
    finally:
        db.close()
