import os
from flask import Flask, send_from_directory
from redis import Redis
from dotenv import load_dotenv
import time

# .env fájl betöltése
load_dotenv()

# Flask app inicializálása
app = Flask(__name__)

# --------------------------------------------------
# MySQL / SQLAlchemy konfiguráció
# --------------------------------------------------
DB_HOST = os.getenv('DB_HOST', 'mysql')
DB_PORT = os.getenv('DB_PORT', '3306')
MYSQL_USER = os.getenv('MYSQL_USER', 'root')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'example')
MYSQL_DB = os.getenv('MYSQL_DB', 'dogs')

app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{DB_HOST}:{DB_PORT}/{MYSQL_DB}"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# --------------------------------------------------
# Redis konfiguráció
# --------------------------------------------------
REDIS_HOST = os.getenv('REDIS_HOST', 'redis')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
redis_client = Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)

# --------------------------------------------------
# QLAlchemy példány importálása az extensions-ből
# --------------------------------------------------
from extensions import db
time.sleep(8)
db.init_app(app)

# --------------------------------------------------
# Blueprint-ek importálása és regisztrálása
# --------------------------------------------------
# belül, app.app_context() alatt importáljuk a routes-okat és regisztráljuk a blueprinteket.
with app.app_context():
    from routes.owners  import owners_bp
    from routes.dogs    import dogs_bp
    from routes.records import records_bp
    from routes.upload  import upload_bp

    app.register_blueprint(owners_bp,  url_prefix='/owners') 
    app.register_blueprint(dogs_bp,    url_prefix='/dogs')
    app.register_blueprint(records_bp, url_prefix='/dogs')
    app.register_blueprint(upload_bp,  url_prefix='/dogs')

    # --------------------------------------------------
    # Feltöltött képek (uploads) kiszolgálása
    # --------------------------------------------------
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    @app.route('/uploads/<path:filename>')
    def uploaded_file(filename):
        return send_from_directory(UPLOAD_FOLDER, filename)

    # --------------------------------------------------
    # DB táblák létrehozása, ha nem léteznek
    # --------------------------------------------------
    db.create_all()

# --------------------------------------------------
# Alkalmazás indítása
# --------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
