from flask import Blueprint, request, jsonify
from extensions import db
from models import Dog, HealthRecord

records_bp = Blueprint('records_bp', __name__)

# --- GET: Egy kutya összes egészségügyi bejegyzése
@records_bp.route('/<int:dog_id>/health_records', methods=['GET'])
def get_health_records(dog_id):
    dog = Dog.query.get(dog_id)
    if not dog:
        return jsonify({"error": "Kutyus nem található"}), 404

    records = HealthRecord.query.filter_by(dog_id=dog_id).order_by(HealthRecord.created_at.desc()).all()
    records_list = [record.to_dict() for record in records]
    return jsonify({"health_records": records_list}), 200

# --- POST: Új egészségügyi bejegyzés hozzáadása
@records_bp.route('/<int:dog_id>/health_records', methods=['POST'])
def create_health_record(dog_id):
    dog = Dog.query.get(dog_id)
    if not dog:
        return jsonify({"error": "Kutyus nem található"}), 404

    data = request.get_json() or {}
    description = data.get('description')
    if not description:
        return jsonify({"error": "Hiányzó leírás"}), 400

    new_record = HealthRecord(dog_id=dog_id, description=description)
    db.session.add(new_record)
    db.session.commit()
    return jsonify(new_record.to_dict()), 201