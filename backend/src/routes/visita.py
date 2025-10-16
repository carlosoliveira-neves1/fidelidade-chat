# backend/src/routes/visita.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from sqlalchemy import select, func, desc
from ..db import SessionLocal
from ..models import Client, Visit

visita_bp = Blueprint("visita_bp", __name__)

@visita_bp.post("/visitas")
@jwt_required()
def registrar_visita():
    """
    Registra uma visita usando cpf OU client_id.
    Resposta: { visit_id, visits_count, eligible }
    """
    data = request.get_json(force=True) or {}
    cpf = (data.get("cpf") or "").strip()
    client_id = data.get("client_id")

    db = SessionLocal()
    try:
        # Encontrar cliente
        cliente = None
        if cpf:
            cliente = db.execute(
                select(Client).where(Client.cpf == cpf)
            ).scalar_one_or_none()
        elif client_id:
            try:
                cliente = db.get(Client, int(client_id))
            except Exception:
                cliente = None

        if not cliente:
            return jsonify({"error": "Cliente não encontrado"}), 404

        # Preferir store_id do cliente; se não houver, tentar do JWT; senão 1
        claims = get_jwt() or {}
        store_id = cliente.store_id or claims.get("store_id") or 1

        # Criar visita
        visita = Visit(client_id=cliente.id, store_id=store_id)
        db.add(visita)
        db.commit()
        db.refresh(visita)

        # Recontar visitas do cliente
        total_visitas = db.execute(
            select(func.count(Visit.id)).where(Visit.client_id == cliente.id)
        ).scalar_one()

        # Elegível (ajuste a regra se precisar)
        elegivel = (total_visitas % 10 == 0)

        return (
            jsonify({
                "visit_id": visita.id,
                "visits_count": int(total_visitas),
                "eligible": elegivel
            }),
            201,
        )
    except Exception as e:
        db.rollback()
        # Não vaza stack trace em produção
        return jsonify({"error": "Falha ao registrar visita"}), 500
    finally:
        db.close()


@visita_bp.get("/visitas")
@jwt_required()
def listar_visitas():
    """
    Lista visitas em ordem decrescente de criação.
    Query params: page (1), per_page (10)
    """
    page = max(1, int(request.args.get("page", 1)))
    per_page = max(1, min(100, int(request.args.get("per_page", 10))))

    db = SessionLocal()
    try:
        total = db.execute(select(func.count(Visit.id))).scalar_one()

        itens = db.execute(
            select(Visit)
            .order_by(desc(Visit.created_at))
            .offset((page - 1) * per_page)
            .limit(per_page)
        ).scalars().all()

        return jsonify({
            "total": int(total),
            "page": page,
            "per_page": per_page,
            "items": [
                {
                    "id": v.id,
                    "client_id": v.client_id,
                    "store_id": v.store_id,
                    "created_at": v.created_at.isoformat()
                }
                for v in itens
            ]
        })
    finally:
        db.close()
