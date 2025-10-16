from __future__ import annotations

import os
import re
from datetime import datetime, timedelta, date
from urllib.parse import quote

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required,
    get_jwt, get_jwt_identity
)
from sqlalchemy import func, select, delete
from sqlalchemy.exc import IntegrityError
from dotenv import load_dotenv

from .db import Base, engine, SessionLocal
from .models import User, Store, Client, Visit, Redemption
from .util import hash_password, verify_password

# importa blueprint de visitas
from .routes.visita import visita_bp

# ================== CONFIG APP ==================
load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "change")
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "change")
app.config["JSON_SORT_KEYS"] = False

# CORS – libera Vercel (prod + previews) e localhost
allowed_origins = [
    "https://fidelidade-chat.vercel.app",
    re.compile(r"https://fidelidade-chat-[a-z0-9-]+\.vercel\.app"),
    "http://localhost:5173",
]
CORS(
    app,
    resources={r"/api/*": {"origins": allowed_origins}},
    supports_credentials=True,
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

jwt = JWTManager(app)

# registra o blueprint de visitas
app.register_blueprint(visita_bp, url_prefix="/api")

# ================== CONSTANTES ==================
STORE_NAMES = [
    "Mega Loja – Jabaquara", "Mascote", "Indianopolis",
    "Tatuape", "Praia Grande", "Bertioga", "Osasco",
]
GIFT_NAME = os.getenv("GIFT_NAME", "1 Kg de Vela Palito")
DEFAULT_META = int(os.getenv("DEFAULT_META", "10"))


# ================= HELPERS =================
def current_user():
    identity = get_jwt_identity()
    if not identity:
        return None
    db = SessionLocal()
    try:
        return db.get(User, int(identity))
    finally:
        db.close()


# ================= AUTH =================
@app.post("/api/auth/login")
def login():
    data = request.get_json(force=True)
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    db = SessionLocal()
    try:
        user = db.execute(select(User).where(User.email == email)).scalar_one_or_none()
        if not user or not verify_password(password, user.password_hash):
            return jsonify({"error": "Credenciais inválidas"}), 401

        claims = {"role": user.role, "lock_loja": user.lock_loja, "store_id": user.store_id}
        token = create_access_token(
            identity=str(user.id),
            additional_claims=claims,
            expires_delta=timedelta(hours=8),
        )
        return jsonify({
            "token": token,
            "user": {
                "id": user.id, "name": user.name, "email": user.email,
                "role": user.role, "lock_loja": user.lock_loja, "store_id": user.store_id
            },
        })
    finally:
        db.close()


@app.get("/api/auth/me")
@jwt_required()
def me():
    user = current_user()
    if not user:
        return jsonify({"error": "not found"}), 404
    return jsonify({
        "id": user.id, "name": user.name, "email": user.email,
        "role": user.role, "lock_loja": user.lock_loja, "store_id": user.store_id
    })


# ================ ADMIN =================
def _require_admin():
    claims = get_jwt()
    return claims.get("role") == "ADMIN"


@app.get("/api/admin/stores")
@jwt_required()
def list_stores():
    if not _require_admin():
        return jsonify({"error": "forbidden"}), 403
    db = SessionLocal()
    try:
        stores = db.execute(select(Store)).scalars().all()
        return jsonify([{"id": s.id, "name": s.name, "meta_visitas": s.meta_visitas} for s in stores])
    finally:
        db.close()


@app.post("/api/admin/users")
@jwt_required()
def create_user():
    if not _require_admin():
        return jsonify({"error": "forbidden"}), 403
    data = request.get_json(force=True)
    db = SessionLocal()
    try:
        store_id = data.get("store_id")
        lock_loja = True if store_id else False
        u = User(
            name=data.get("name", "").strip(),
            email=data.get("email", "").strip().lower(),
            password_hash=hash_password(data.get("password", "")),
            role=data.get("role", "ATENDENTE"),
            lock_loja=lock_loja,
            store_id=store_id,
        )
        db.add(u)
        db.commit()
        return jsonify({
            "id": u.id, "name": u.name, "email": u.email,
            "role": u.role, "lock_loja": u.lock_loja, "store_id": u.store_id
        }), 201
    except IntegrityError:
        db.rollback()
        return jsonify({"error": "email já existe"}), 400
    finally:
        db.close()


@app.get("/api/admin/users")
@jwt_required()
def list_users():
    if not _require_admin():
        return jsonify({"error": "forbidden"}), 403
    db = SessionLocal()
    try:
        items = db.execute(select(User).order_by(User.id.desc())).scalars().all()
        return jsonify([
            {
                "id": u.id, "name": u.name, "email": u.email,
                "role": u.role, "lock_loja": u.lock_loja, "store_id": u.store_id
            } for u in items
        ])
    finally:
        db.close()


# =============== CLIENTES ===============
@app.post("/api/clientes")
@jwt_required()
def create_client():
    user = current_user()
    data = request.get_json(force=True)
    db = SessionLocal()
    try:
        raw_bday = data.get("birthday")
        bday_str = None
        if raw_bday:
            try:
                bday_str = date.fromisoformat(str(raw_bday)).isoformat()
            except Exception:
                return jsonify({"error": "birthday inválido. Use YYYY-MM-DD"}), 400

        c = Client(
            name=data.get("name", "").strip(),
            cpf=(data.get("cpf") or "").strip(),
            phone=(data.get("phone") or "").strip(),
            email=(data.get("email") or "").strip() or None,
            birthday=bday_str,
            store_id=(data.get("store_id") or user.store_id),
        )
        db.add(c)
        db.commit()
        return jsonify({"id": c.id}), 201
    except IntegrityError:
        db.rollback()
        return jsonify({"error": "CPF já cadastrado"}), 400
    finally:
        db.close()


@app.get("/api/clientes")
@jwt_required()
def list_clients():
    user = current_user()
    cpf = (request.args.get("cpf") or "").strip()
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 10))
    db = SessionLocal()
    try:
        q = select(Client)
        if cpf:
            q = q.where(Client.cpf == cpf)
        elif user.lock_loja and user.store_id:
            q = q.where(Client.store_id == user.store_id)
        total = db.execute(select(func.count()).select_from(q.subquery())).scalar_one()
        items = db.execute(
            q.order_by(Client.created_at.desc())
             .offset((page - 1) * per_page)
             .limit(per_page)
        ).scalars().all()
        return jsonify({
            "total": int(total),
            "items": [{
                "id": c.id, "name": c.name, "cpf": c.cpf, "phone": c.phone,
                "email": c.email, "birthday": c.birthday,
                "store_id": c.store_id,
            } for c in items],
        })
    finally:
        db.close()


# =============== RESGATES ===============
@app.post("/api/resgates")
@jwt_required()
def redeem_gift():
    user = current_user()
    data = request.get_json(force=True)
    cpf = (data.get("cpf") or "").strip()
    gift_name = (data.get("gift_name") or GIFT_NAME).strip()
    db = SessionLocal()
    try:
        c = db.execute(select(Client).where(Client.cpf == cpf)).scalar_one_or_none()
        if not c:
            return jsonify({"error": "Cliente não encontrado"}), 404

        store_id = user.store_id or c.store_id
        if not store_id:
            st = db.execute(select(Store).order_by(Store.id.asc())).scalars().first()
            store_id = st.id if st else None

        store = db.get(Store, store_id) if store_id else None
        meta = store.meta_visitas if store else DEFAULT_META

        count_visits = db.execute(select(func.count(Visit.id)).where(Visit.client_id == c.id)).scalar_one()
        if count_visits < meta:
            return jsonify({
                "error": "Cliente ainda não atingiu a meta",
                "visits_count": int(count_visits), "meta": int(meta),
            }), 400

        r = Redemption(client_id=c.id, store_id=store_id, gift_name=gift_name)
        db.add(r)
        db.commit()

        db.execute(delete(Visit).where(Visit.client_id == c.id))
        db.commit()

        return jsonify({
            "redemption_id": r.id, "gift_name": r.gift_name,
            "when": r.created_at.isoformat(), "store_id": store_id,
        })
    finally:
        db.close()


# =============== DASHBOARD ===============
@app.get("/api/dashboard/kpis")
@jwt_required()
def kpis():
    user = current_user()
    db = SessionLocal()
    try:
        since = datetime.utcnow() - timedelta(days=30)
        vq = select(func.count(Visit.id)).where(Visit.created_at >= since)
        rq = select(func.count(Redemption.id)).where(Redemption.created_at >= since)
        cq = select(func.count(Client.id))
        if user.lock_loja and user.store_id:
            vq = vq.where(Visit.store_id == user.store_id)
            rq = rq.where(Redemption.store_id == user.store_id)
            cq = cq.where(Client.store_id == user.store_id)
        visits_30 = db.execute(vq).scalar_one()
        redemptions_30 = db.execute(rq).scalar_one()
        clients_total = db.execute(cq).scalar_one()
        return jsonify({
            "visitas_30d": int(visits_30),
            "clientes_total": int(clients_total),
            "resgates_30d": int(redemptions_30),
        })
    finally:
        db.close()


@app.get("/api/dashboard/aniversariantes")
@jwt_required()
def birthday_list():
    user = current_user()
    mes = datetime.utcnow().month
    db = SessionLocal()
    try:
        month_expr = func.extract("month", func.to_date(Client.birthday, 'YYYY-MM-DD'))
        q = select(Client).where(month_expr == mes)
        if user.lock_loja and user.store_id:
            q = q.where(Client.store_id == user.store_id)
        items = db.execute(q).scalars().all()
        return jsonify([{
            "id": c.id, "name": c.name, "cpf": c.cpf,
            "birthday": c.birthday,
        } for c in items])
    finally:
        db.close()


# =============== HEALTH & SEED ===============
@app.get("/api/_health")
def health_api():
    return {"status": "ok"}


@app.route("/api/_setup/seed", methods=["POST", "GET"])
def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        for nm in STORE_NAMES:
            ex = db.execute(select(Store).where(Store.name == nm)).scalar_one_or_none()
            if not ex:
                db.add(Store(name=nm, meta_visitas=DEFAULT_META))
        db.commit()

        admin = db.execute(select(User).where(User.email == "admin@cdc.com")).scalar_one_or_none()
        if not admin:
            admin = User(
                name="Admin", email="admin@cdc.com",
                password_hash=hash_password("123456"),
                role="ADMIN", lock_loja=False, store_id=None,
            )
            db.add(admin); db.commit()

        mascote = db.execute(select(Store).where(Store.name == "Mascote")).scalar_one_or_none()
        if mascote:
            gerente = db.execute(
                select(User).where(User.email == "gerente.mascote@cdc.com")
            ).scalar_one_or_none()
            if not gerente:
                gerente = User(
                    name="Gerente Mascote", email="gerente.mascote@cdc.com",
                    password_hash=hash_password("123456"),
                    role="GERENTE", lock_loja=True, store_id=mascote.id,
                )
                db.add(gerente); db.commit()

        return {"ok": True, "admin_login": "admin@cdc.com", "password": "123456"}
    finally:
        db.close()


# =============== BOOT (local) ===============
if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    app.run(host="127.0.0.1", port=5000, debug=True)
