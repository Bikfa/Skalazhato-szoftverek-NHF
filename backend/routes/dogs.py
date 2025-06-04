from flask import Blueprint, request, jsonify
from extensions import db
from models import Owner, Dog
from cache import clear_cached_owners

dogs_bp = Blueprint('dogs_bp', __name__)

# --- POST: Új kutya hozzáadása egy gazdihoz
@dogs_bp.route('/owners/<int:owner_id>/dogs', methods=['POST'])
def create_dog(owner_id):
    owner = Owner.query.get(owner_id)
    if not owner:
        return jsonify({"error": "Gazdi nem található"}), 404

    data = request.get_json() or {}
    name   = data.get('name')
    breed = data.get('breed')
    color = data.get('color')
    gender = data.get('gender')
    # health_record mezőt opcionálisan elfogad a backend, de itt üresen küldjük
    if not breed or not color or not gender or not name:
        return jsonify({"error": "Hiányzó adatok"}), 400

    new_dog = Dog(
        name=name,
        breed=breed,
        color=color,
        gender=gender,
        owner_id=owner_id
    )
    db.session.add(new_dog)
    db.session.commit()

    clear_cached_owners()

    return jsonify(new_dog.to_dict()), 201

# --- GET: Egyedi kutya lekérése szerkesztési célból
@dogs_bp.route('/<int:dog_id>', methods=['GET'])
def get_dog(dog_id):
    dog = Dog.query.get(dog_id)
    if not dog:
        return jsonify({"error": "Kutyus nem található"}), 404
    return jsonify(dog.to_dict()), 200

# --- PUT: Kutyus adatainak frissítése
@dogs_bp.route('/<int:dog_id>', methods=['PUT'])
def update_dog(dog_id):
    dog = Dog.query.get(dog_id)
    if not dog:
        return jsonify({"error": "Kutyus nem található"}), 404

    data = request.get_json() or {}
    name = data.get('name')
    breed = data.get('breed')
    color = data.get('color')
    gender = data.get('gender')
    # health_record mezőt opcionálisan elfogad a backend, de itt nem használjuk
    if not breed or not color or not gender or not name:
        return jsonify({"error": "Hiányzó adatok"}), 400

    dog.name = name
    dog.breed = breed
    dog.color = color
    dog.gender = gender
    db.session.commit()

    clear_cached_owners()

    return jsonify(dog.to_dict()), 200

# --- DELETE: Kutyus törlése
@dogs_bp.route('/<int:dog_id>', methods=['DELETE'])
def delete_dog(dog_id):
    dog = Dog.query.get(dog_id)
    if not dog:
        return jsonify({"error": "Kutyus nem található"}), 404

    db.session.delete(dog)
    db.session.commit()
    clear_cached_owners()
    return jsonify({"message": "Kutyus törölve"}), 200