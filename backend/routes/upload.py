from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from extensions import db
from models import Dog
import os
from cache import clear_cached_owners

upload_bp = Blueprint('upload_bp', __name__)

# Engedélyezett képkiterjesztések
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return (
        '.' in filename
        and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    )

# --- POST: Kutyus képének feltöltése
@upload_bp.route('/<int:dog_id>/upload_image', methods=['POST'])
def upload_image(dog_id):
    # Először is lekérdezzük a Dog objektumot
    dog = Dog.query.get(dog_id)
    if not dog:
        return jsonify({"error": "Kutyus nem található"}), 404

    # Ellenőrizzük, hogy tényleg küldtek-e fájlt
    if 'image' not in request.files:
        return jsonify({"error": "Nincs feltöltött fájl"}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "Nincs kiválasztott fájl"}), 400

    # Ellenőrizzük a kiterjesztést
    if not allowed_file(file.filename):
        return jsonify({"error": "Nem engedélyezett fájlformátum"}), 400

    # Mivel engedélyezett a fájl, akkor elmentjük
    filename = secure_filename(file.filename)

    # A kötelező upload-mappa: app indításkor vagy itt győződjünk meg róla, hogy létezik
    upload_folder = current_app.config.get(
        'UPLOAD_FOLDER',
        os.path.join(os.getcwd(), 'uploads')
    )
    os.makedirs(upload_folder, exist_ok=True)

    save_path = os.path.join(upload_folder, filename)
    file.save(save_path)

    # Ezután a Dog objektum image_path mezőjét frissítjük, és elmentjük az adatbázisba
    # Itt a tárolt útvonal relatív útvonalként: uploads/filename.jpg
    dog.image_path = os.path.join('uploads', filename)
    db.session.commit()

    clear_cached_owners()
    
    return jsonify({"image_path": dog.image_path}), 201
