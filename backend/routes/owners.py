from flask import Blueprint, request, jsonify
from extensions import db
from models import Owner
from cache import get_cached_owners, set_cached_owners, clear_cached_owners

owners_bp = Blueprint('owners_bp', __name__)

# --- GET: Minden gazdi lekérése (cache-elve)
@owners_bp.route('/', methods=['GET'])
def get_owners():
    cached = get_cached_owners()
    if cached is not None:
        return jsonify({"owners": cached, "redis": True}), 200

    owners = Owner.query.order_by(Owner.id.asc()).all()
    owners_list = [owner.to_dict() for owner in owners]
    set_cached_owners(owners_list)
    return jsonify({"owners": owners_list, "redis": False}), 200

# --- POST: Új gazdi létrehozása
@owners_bp.route('/', methods=['POST'])
def create_owner():
    data = request.get_json() or {}
    email = data.get('email')
    password = data.get('password')
    name     = data.get('name')
    if not email or not password or not name:
        return jsonify({"error": "Hiányzó adatok"}), 400

    if Owner.query.filter_by(email=email).first():
        return jsonify({"error": "Ez az email már létezik"}), 409

    new_owner = Owner(email=email, password=password, name=name)
    db.session.add(new_owner)
    db.session.commit()
    clear_cached_owners()
    return jsonify(new_owner.to_dict()), 201

# --- GET: Egy gazdi lekérése ID alapján
@owners_bp.route('/<int:owner_id>', methods=['GET'])
def get_owner(owner_id):
    owner = Owner.query.get(owner_id)
    if not owner:
        return jsonify({"error": "Gazdi nem található"}), 404
    return jsonify(owner.to_dict()), 200

# --- PUT: Egy gazdi frissítése
@owners_bp.route('/<int:owner_id>', methods=['PUT', 'POST'])
def update_owner(owner_id):
    print('Itt vagyoook')
    owner = Owner.query.get(owner_id)
    if not owner:
        return jsonify({"error": "Gazdi nem található"}), 404

    data = request.get_json() or {}
    email = data.get('email')
    password = data.get('password')
    name     = data.get('name')
    if not email or not name:
        return jsonify({"error": "Hiányzó adatok"}), 400
    
    if password:
        owner.password = password

    if email != owner.email and Owner.query.filter_by(email=email).first():
        return jsonify({"error": "Ez az email már létezik"}), 409

    owner.email = email
    owner.name     = name 
    db.session.commit()
    clear_cached_owners()
    return jsonify(owner.to_dict()), 200

# --- DELETE: Egy gazdi törlése
@owners_bp.route('/<int:owner_id>', methods=['DELETE'])
def delete_owner(owner_id):
    owner = Owner.query.get(owner_id)
    if not owner:
        return jsonify({"error": "Gazdi nem található"}), 404

    db.session.delete(owner)
    db.session.commit()
    clear_cached_owners()
    return jsonify({"message": "Gazdi törölve"}), 200