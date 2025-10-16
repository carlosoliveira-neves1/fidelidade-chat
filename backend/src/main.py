# src/main.py
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
from . import emailer  # mantém como está no projeto

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "change-this-in-prod")
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "jwt-secret-change-me")
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

STORE_NAMES = [
    "Mega Loja – Jabaquara", "Mascote", "Indianopolis",
    "Tatuape", "Praia Grande", "Bertioga", "Osasco",
]
GIFT_NAME = os.getenv("GIFT_NAME", "1 Kg de Vela Palito")
DEFAULT_META = int(os.getenv("DEFAULT_META", "10"))


def current_user() -> User | None:
    """Carrega o usuário logado a partir do JWT."""
    identity = get_jwt_identity()
    if not identity:
        return None
    db = SessionLocal()
    try:
        return db.get(User, int(identity))
    finally:
        db.close()


# =============== HEALTH ===============
@app.get("/api/_health")
def health_api():
    return {"status": "ok"}


@app.get("/_health")
def health_root():
    return {"status": "ok"}


# =============== AUTH ===============
@app.post("/api/auth/login")
def login():
    data = request.get_json(force=True)
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    db = SessionLocal()
    try:
        user = db.execute(select(User).where(User.email == email)).scalar_one_or_none()
        if not user or not verify_password(password, user.password_hash):
            return jsonify({"error": "Credenciais inválidas"}), 401

        claims = {
            "role": user.role,
            "lock_loja": user.lock_loja,
            "store_id": user.store_id,
        }
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


# =============== ADMIN ===============
def _require_admin() -> bool:
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
        return jsonify([
            {"id": s.id, "name": s.name, "meta_visitas": s.meta_visitas}
            for s in stores
        ])
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
            name=(data.get("name") or "").strip(),
            email=(data.get("email") or "").strip().lower(),
            password_hash=hash_password(data.get("password") or ""),
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


@app.put("/api/admin/users/<int:uid>")
@jwt_required()
def update_user(uid: int):
    if not _require_admin():
        return jsonify({"error": "forbidden"}), 403

    data = request.get_json(force=True)
    db = SessionLocal()
    try:
        u = db.get(User, uid)
        if not u:
            return jsonify({"error": "not found"}), 404

        u.name = (data.get("name", u.name) or "").strip()

        new_email = (data.get("email", u.email) or "").strip().lower()
        if new_email != u.email:
            exists = db.execute(
                select(User).where(User.email == new_email, User.id != u.id)
            ).scalar_one_or_none()
            if exists:
                return jsonify({"error": "email já existe"}), 400
            u.email = new_email

        u.role = data.get("role", u.role)
        u.store_id = data.get("store_id", u.store_id)
        u.lock_loja = True if u.store_id else False

        if data.get("password"):
            u.password_hash = hash_password(data["password"])

        db.commit()
        return jsonify({"ok": True})
    finally:
        db.close()


@app.delete("/api/admin/users/<int:uid>")
@jwt_required()
def delete_user(uid: int):
    if not _require_admin():
        return jsonify({"error": "forbidden"}), 403
    db = SessionLocal()
    try:
        u = db.get(User, uid)
        if not u:
            return jsonify({"error": "not found"}), 404
        db.delete(u)
        db.commit()
        return jsonify({"ok": True})
    finally:
        db.close()


# =============== CLIENTES ===============
@app.post("/api/clientes")
@jwt_required()
def create_client():
    """Cria cliente. Converte birthday (string ISO YYYY-MM-DD) para date."""
    user = current_user()
    data = request.get_json(force=True)

    db = SessionLocal()
    try:
        bday: date | None = None
        if data.get("birthday"):
            # <- ESTE É O AJUSTE QUE EVITA O ERRO DE 'varchar -> date'
            bday = date.fromisoformat(str(data["birthday"]))

        c = Client(
            name=(data.get("name") or "").strip(),
            cpf=(data.get("cpf") or "").strip(),
            phone=(data.get("phone") or "").strip(),
            email=((data.get("email") or "").strip() or None),
            birthday=bday,
            store_id=(data.get("store_id") or (user.store_id if user else None)),
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
        elif user and user.lock_loja and user.store_id:
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
                "email": c.email, "birthday": (c.birthday.isoformat() if c.birthday else None),
                "store_id": c.store_id,
            } for c in items],
        })
    finally:
        db.close()


# =============== HELPERS (WA) ===============
def _format_phone_to_wa(phone: str) -> str | None:
    if not phone:
        return None
    digits = "".join(ch for ch in phone if ch.isdigit())
    if len(digits) < 10:
        return None
    if not digits.startswith("55"):
        digits = "55" + digits
    return digits


# =============== VISITAS ===============
@app.post("/api/visitas")
@jwt_required()
def register_visit():
    user = current_user()
    data = request.get_json(force=True)
    cpf = (data.get("cpf") or "").strip()

    db = SessionLocal()
    try:
        c = db.execute(select(Client).where(Client.cpf == cpf)).scalar_one_or_none()
        if not c:
            return jsonify({"error": "Cliente não encontrado"}), 404

        store_id = user.store_id or c.store_id if user else c.store_id
        if not store_id:
            st = db.execute(select(Store).order_by(Store.id.asc())).scalars().first()
            store_id = st.id if st else None

        v = Visit(client_id=c.id, store_id=store_id)
        db.add(v)
        db.commit()

        count_visits = db.execute(
            select(func.count(Visit.id)).where(Visit.client_id == c.id)
        ).scalar_one()

        store = db.get(Store, store_id) if store_id else None
        meta = store.meta_visitas if store else DEFAULT_META
        eligible = count_visits >= meta
        faltam = max(0, meta - count_visits)

        # E-mail (opcional)
        titulo = "Sua pontuação - Programa de Fidelidade Casa do Cigano"
        texto_email = (
            f"Olá {c.name},\n\nVocê agora tem {count_visits} visita(s). Meta para brinde: {meta}. "
        )
        if eligible:
            texto_email += f"Você JÁ PODE resgatar seu brinde ({GIFT_NAME})!"
        else:
            texto_email += f"Faltam {faltam} visita(s) para o próximo brinde ({GIFT_NAME})."
        texto_email += "\n\nObrigado pela visita!"

        html = f"""
        <p>Olá <b>{c.name}</b>,</p>
        <p>Você agora tem <b>{count_visits}</b> visita(s). Meta para brinde: <b>{meta}</b>.</p>
        <p>{
            'Você <b>JÁ PODE</b> resgatar seu brinde ('+GIFT_NAME+')!'
            if eligible
            else f'Faltam <b>{faltam}</b> visita(s) para o próximo brinde ('+GIFT_NAME+').'
        }</p>
        <p>Obrigado pela visita!<br/>Casa do Cigano</p>
        """

        TEST_EMAIL_TO = os.getenv("TEST_EMAIL_TO", "").strip()
        to_email = (c.email or "").strip() or TEST_EMAIL_TO
        if to_email:
            try:
                emailer.send_email(to_email, titulo, texto_email, html)
            except Exception:
                # não falha a request se o e-mail falhar
                pass

        # WhatsApp
        wa = None
        if c.phone:
            digits = _format_phone_to_wa(c.phone)
            if digits:
                primeiro_nome = (c.name or "cliente").strip().split()[0]
                if eligible:
                    msg = (
                        f"Oi, {primeiro_nome}! Obrigado por confiar na Casa do Cigano.\n\n"
                        f"Esperamos que você ame seu novo produto!\n\n"
                        f"Você está participando do nosso programa de fidelidade *CiganoLovers* e você tem {int(count_visits)} visita(s).\n\n"
                        f"Você JÁ PODE resgatar seu brinde: {GIFT_NAME} (meta {int(meta)} visitas).\n\n"
                        "Confira as novidades em nossa loja: https://www.casadocigano.com.br/"
                    )
                else:
                    msg = (
                        f"Oi, {primeiro_nome}! Obrigado por confiar na Casa do Cigano.\n\n"
                        f"Esperamos que você ame seu novo produto!\n\n"
                        f"Você está participando do nosso programa de fidelidade *CiganoLovers* e você tem {int(count_visits)} visita(s).\n\n"
                        f"Faltam {int(faltam)} visita(s) para o brinde {GIFT_NAME} (meta {int(meta)} visitas).\n\n"
                        "Confira as novidades em nossa loja: https://www.casadocigano.com.br/"
                    )
                wa = f"https://wa.me/{digits}?text=" + quote(msg, safe="", encoding="utf-8")

        return jsonify({
            "visit_id": v.id,
            "visits_count": int(count_visits),
            "meta": int(meta),
            "eligible": bool(eligible),
            "store_id": store_id,
            "client": {
                "id": c.id, "name": c.name, "cpf": c.cpf, "phone": c.phone, "email": c.email,
            },
            "whatsapp_url": wa,
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

        store_id = user.store_id or c.store_id if user else c.store_id
        if not store_id:
            st = db.execute(select(Store).order_by(Store.id.asc())).scalars().first()
            store_id = st.id if st else None

        store = db.get(Store, store_id) if store_id else None
        meta = store.meta_visitas if store else DEFAULT_META

        count_visits = db.execute(
            select(func.count(Visit.id)).where(Visit.client_id == c.id)
        ).scalar_one()

        if count_visits < meta:
            return jsonify({
                "error": "Cliente ainda não atingiu a meta",
                "visits_count": int(count_visits),
                "meta": int(meta),
            }), 400

        r = Redemption(client_id=c.id, store_id=store_id, gift_name=gift_name)
        db.add(r)
        db.commit()

        # Zera visitas após o resgate
        db.execute(delete(Visit).where(Visit.client_id == c.id))
        db.commit()

        return jsonify({
            "redemption_id": r.id,
            "gift_name": r.gift_name,
            "when": r.created_at.isoformat(),
            "store_id": store_id,
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

        if user and user.lock_loja and user.store_id:
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
        q = select(Client).where(func.extract("month", Client.birthday) == mes)
        if user and user.lock_loja and user.store_id:
            q = q.where(Client.store_id == user.store_id)

        items = db.execute(q).scalars().all()
        return jsonify([{
            "id": c.id,
            "name": c.name,
            "cpf": c.cpf,
            "birthday": (c.birthday.isoformat() if c.birthday else None),
        } for c in items])
    finally:
        db.close()


# =============== SEED (idempotente) ===============
@app.route("/api/_setup/seed", methods=["POST", "GET"])
def seed():
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # Lojas padrão
        for nm in STORE_NAMES:
            ex = db.execute(select(Store).where(Store.name == nm)).scalar_one_or_none()
            if not ex:
                db.add(Store(name=nm, meta_visitas=DEFAULT_META))
        db.commit()

        # Admin
        admin = db.execute(select(User).where(User.email == "admin@cdc.com")).scalar_one_or_none()
        if not admin:
            admin = User(
                name="Admin",
                email="admin@cdc.com",
                password_hash=hash_password("123456"),
                role="ADMIN",
                lock_loja=False,
                store_id=None,
            )
            db.add(admin)
            db.commit()

        # Gerente exemplo (Mascote)
        mascote = db.execute(select(Store).where(Store.name == "Mascote")).scalar_one()
        gerente = db.execute(
            select(User).where(User.email == "gerente.mascote@cdc.com")
        ).scalar_one_or_none()
        if not gerente:
            gerente = User(
                name="Gerente Mascote",
                email="gerente.mascote@cdc.com",
                password_hash=hash_password("123456"),
                role="GERENTE",
                lock_loja=True,
                store_id=mascote.id,
            )
            db.add(gerente)
            db.commit()

        return {"ok": True, "admin_login": "admin@cdc.com", "password": "123456"}
    finally:
        db.close()


# =============== BOOT LOCAL ===============
if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    app.run(host="127.0.0.1", port=5000, debug=True)

# gunicorn alvo (Render): "src.main:app"
