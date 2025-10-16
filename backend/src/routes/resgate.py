from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy import select, func, desc, delete
from ..db import SessionLocal
from ..models import Client, Redemption, Visit, Store

resgate_bp = Blueprint("resgate_bp", __name__)

@resgate_bp.post("/resgates")
@jwt_required()
def criar_resgate():
    data = request.get_json(force=True)
    cpf = (data.get("cpf") or "").strip()
    client_id = data.get("client_id")
    gift_name = (data.get("gift_name") or "Brinde").strip()
    db = SessionLocal()
    try:
        c = None
        if cpf:
            c = db.execute(select(Client).where(Client.cpf == cpf)).scalar_one_or_none()
        elif client_id:
            c = db.get(Client, int(client_id))
        if not c:
            return jsonify({"error": "Cliente não encontrado"}), 404
        r = Redemption(client_id=c.id, store_id=c.store_id, gift_name=gift_name)
        db.add(r)
        db.commit()
        db.execute(delete(Visit).where(Visit.client_id == c.id))
        db.commit()
        return jsonify({"redemption_id": r.id, "gift_name": r.gift_name, "when": r.created_at.isoformat()}), 201
    finally:
        db.close()

@resgate_bp.get("/resgates")
@jwt_required()
def listar_resgates():
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 10))
    db = SessionLocal()
    try:
        q = select(Redemption).order_by(desc(Redemption.created_at))
        total = db.execute(select(func.count()).select_from(q.subquery())).scalar_one()
        items = db.execute(q.offset((page-1)*per_page).limit(per_page)).scalars().all()
        return jsonify({"total": int(total), "items": [{"id": r.id, "gift_name": r.gift_name, "created_at": r.created_at.isoformat()} for r in items]})
    finally:
        db.close()
