import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
import requests
from dotenv import load_dotenv

# .env beolvasása
load_dotenv()

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'alapertelmezett_titkos')

# Auth Gateway URL (Docker Compose-ben: auth_gw:4000)
AUTH_URL = os.getenv('AUTH_URL', 'http://auth_gw:4000')
# API_URL  = os.getenv('API_URL',  'http://dog_project-backend:5000')
API_URL = "http://auth_gw:4000"

# ----------------------------------------
# Minden sablonba injektáljuk, hogy belépve van-e a felhasználó
# ----------------------------------------
@app.context_processor
def inject_user():
    return {
        'is_logged_in': 'token' in session
    }

def get_auth_headers():
    return {
        'Authorization': f"Bearer {session.get('token')}"
    }

# ----------------------------------------
# Bejelentkezés / kilépés
# ----------------------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        # Hitelesítő kérés az auth_gw /auth végpontra
        resp = requests.post(f"{AUTH_URL}/auth", json={
            'email': email,
            'password': password
        })
        if resp.status_code == 200:
            data = resp.json()
            session['token'] = data.get('token')
            return redirect(url_for('index'))
        flash('Hibás e-mail vagy jelszó', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('token', None)
    return redirect(url_for('login'))

# ----------------------------------------
# Főoldal: Gazdik és Kutyusok listázása
# ----------------------------------------
@app.route('/')
def index():
    if 'token' not in session:
        return redirect(url_for('login'))

    # GET /owners a proxy-n keresztül (auth_gw-n), tokennel
    resp = requests.get(
        f"{API_URL}/owners",
        headers=get_auth_headers()
    )
    if resp.status_code != 200:
        flash('Nem sikerült betölteni a gazdikat', 'danger')
        return render_template('index.html', owners=[], redis=False)

    data = resp.json()
    owners = data.get('owners', [])
    redis_used = data.get('redis', False)
    return render_template('index.html', owners=owners, redis=redis_used)

# ----------------------------------------
# Új gazdi űrlap és mentés
# ----------------------------------------
@app.route('/owners/new', methods=['GET'])
def owners_new_form():
    if 'token' not in session:
        return redirect(url_for('login'))
    return render_template('add_owner.html')

@app.route('/owners/new', methods=['POST'])
def create_owner():
    if 'token' not in session:
        return redirect(url_for('login'))
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')
    payload = {'email': email, 'password': password, 'name': name}
    resp = requests.post(
        f"{API_URL}/owners",
        json=payload,
        headers=get_auth_headers()
    )
    if resp.status_code != 201:
        try:
            error = resp.json().get('error', 'Ismeretlen hiba')
        except Exception:
            error = f"Hiba: {resp.status_code} – nem várt válasz."
        return render_template('add_owner.html', error=error)
    return redirect(url_for('index'))

# ----------------------------------------
# Gazdi szerkesztése (GET űrlap)
# ----------------------------------------
@app.route('/owners/<int:owner_id>/edit', methods=['GET'])
def edit_owner_form(owner_id):
    if 'token' not in session:
        return redirect(url_for('login'))
    resp = requests.get(
        f"{API_URL}/owners/{owner_id}",
        headers=get_auth_headers()
    )
    if resp.status_code != 200:
        flash('Nem található a gazdi', 'danger')
        return redirect(url_for('index'))
    owner = resp.json()
    return render_template('edit_owner.html', owner=owner)

# ----------------------------------------
# Gazdi szerkesztés mentése
# ----------------------------------------
@app.route('/owners/<int:owner_id>/edit', methods=['POST'])
def update_owner(owner_id):
    breakpoint()
    if 'token' not in session:
        return redirect(url_for('login'))

    name     = request.form.get('name')
    email    = request.form.get('email')
    password = request.form.get('password')

    payload = {'email': email, 'password': password, 'name': name}

    resp = requests.put(
        f"{API_URL}/owners/{owner_id}",
        json=payload,
        headers=get_auth_headers()
    )

    if resp.status_code != 200:
        try:
            error = resp.json().get('error', 'Ismeretlen hiba')
        except Exception:
            error = f"Hiba: {resp.status_code} – nem várt válasz."
        owner = {'id': owner_id, 'email': email, 'password': password, 'name': name}
        return render_template('edit_owner.html', owner=owner, error=error)

    return redirect(url_for('index'))

# ----------------------------------------
# Gazdi törlése
# ----------------------------------------
@app.route('/owners/<int:owner_id>/delete', methods=['POST'])
def delete_owner(owner_id):
    if 'token' not in session:
        return redirect(url_for('login'))
    requests.delete(
        f"{API_URL}/owners/{owner_id}",
        headers=get_auth_headers()
    )
    return redirect(url_for('index'))

# ----------------------------------------
# Új kutya hozzáadása űrlap (GET)
# ----------------------------------------
@app.route('/owners/<int:owner_id>/dogs/new', methods=['GET'])
def add_dog_form(owner_id):
    if 'token' not in session:
        return redirect(url_for('login'))
    return render_template('add_dog.html', owner_id=owner_id)

# ----------------------------------------
# Új kutya mentése (POST)
# ----------------------------------------
@app.route('/owners/<int:owner_id>/dogs/new', methods=['POST'])
def create_dog(owner_id):
    if 'token' not in session:
        return redirect(url_for('login'))
    name   = request.form.get('name')
    breed  = request.form.get('breed')
    color  = request.form.get('color')
    gender = request.form.get('gender')

    payload = {
        'name': name,
        'breed': breed,
        'color': color,
        'gender': gender
    }

    resp = requests.post(
        f"{API_URL}/dogs/owners/{owner_id}/dogs",
        json=payload,
        headers=get_auth_headers()
    )

    if resp.status_code != 201:
        try:
            error = resp.json().get('error', 'Ismeretlen hiba')
        except Exception:
            error = f"Hiba: {resp.status_code} – nem várt válasz."
        return render_template('add_dog.html', owner_id=owner_id, error=error)

    return redirect(url_for('index'))

# ----------------------------------------
# Kutya szerkesztő űrlap (GET)
# ----------------------------------------
@app.route('/dogs/<int:dog_id>/edit', methods=['GET'])
def edit_dog_form(dog_id):
    if 'token' not in session:
        return redirect(url_for('login'))
    resp = requests.get(
        f"{API_URL}/dogs/{dog_id}",
        headers=get_auth_headers()
    )
    if resp.status_code != 200:
        flash('Nem található a kutya', 'danger')
        return redirect(url_for('index'))
    dog = resp.json()
    return render_template('edit_dog.html', dog=dog)

# ----------------------------------------
# Kutya szerkesztés mentése
# ----------------------------------------
@app.route('/dogs/<int:dog_id>/edit', methods=['POST'])
def update_dog(dog_id):
    if 'token' not in session:
        return redirect(url_for('login'))
    name = request.form.get('name')
    breed = request.form.get('breed')
    color = request.form.get('color')
    gender = request.form.get('gender')
    # health_record már máshol van kezelve
    payload = {
        'name':name,
        'breed': breed,
        'color': color,
        'gender': gender
    }
    resp = requests.put(
        f"{API_URL}/dogs/{dog_id}",
        json=payload,
        headers=get_auth_headers()
    )
    if resp.status_code != 200:
        try:
            error = resp.json().get('error', 'Ismeretlen hiba')
        except Exception:
            error = f"Hiba: {resp.status_code} – nem várt válasz."

        dog = {
            'name':name,
            'id': dog_id,
            'breed': breed,
            'color': color,
            'gender': gender
        }
        return render_template('edit_dog.html', dog=dog, error=error)
    return redirect(url_for('index'))

# ----------------------------------------
# Kutya törlése (POST)
# ----------------------------------------
@app.route('/dogs/<int:dog_id>/delete', methods=['POST'])
def delete_dog(dog_id):
    if 'token' not in session:
        return redirect(url_for('login'))
    requests.delete(
        f"{API_URL}/dogs/{dog_id}",
        headers=get_auth_headers()
    )
    return redirect(url_for('index'))

# ----------------------------------------
# Egészségügyi napló (listázás és új bejegyzés)
# ----------------------------------------
@app.route('/dogs/<int:dog_id>/health', methods=['GET'])
def health_form(dog_id):
    if 'token' not in session:
        return redirect(url_for('login'))

    # Lekérjük a HealthRecord-eket
    resp = requests.get(
        f"{API_URL}/dogs/{dog_id}/health_records",
        headers=get_auth_headers()
    )
    if resp.status_code != 200:
        flash('Nem sikerült betölteni az egészségügyi naplót', 'danger')
        return redirect(url_for('index'))

    data = resp.json()
    records = data.get('health_records', [])
    return render_template('dog_health.html', dog_id=dog_id, records=records)

@app.route('/dogs/<int:dog_id>/health', methods=['POST'])
def create_health_record(dog_id):
    if 'token' not in session:
        return redirect(url_for('login'))

    description = request.form.get('description')
    if not description:
        flash('A leírás nem lehet üres', 'danger')
        return redirect(url_for('health_form', dog_id=dog_id))

    payload = {'description': description}
    resp = requests.post(
        f"{API_URL}/dogs/{dog_id}/health_records",
        json=payload,
        headers=get_auth_headers()
    )
    if resp.status_code != 201:
        try:
            error = resp.json().get('error', 'Ismeretlen hiba')
        except Exception:
            error = f"Hiba: {resp.status_code} – nem várt válasz."
        flash(error, 'danger')
        return redirect(url_for('health_form', dog_id=dog_id))

    return redirect(url_for('health_form', dog_id=dog_id))

# ----------------------------------------
# Kép feltöltő űrlap (GET)
# ----------------------------------------
@app.route('/dogs/<int:dog_id>/upload', methods=['GET'])
def upload_form(dog_id):
    if 'token' not in session:
        return redirect(url_for('login'))
    return render_template('upload_image.html', dog_id=dog_id)

# ----------------------------------------
# Kép feltöltés kezelése (POST)
# ----------------------------------------
@app.route('/dogs/<int:dog_id>/upload', methods=['POST'])
def upload_image(dog_id):
    if 'token' not in session:
        return redirect(url_for('login'))

    if 'image' not in request.files:
        return render_template('upload_image.html', dog_id=dog_id, error="Nincs feltöltendő kép!")
    image = request.files['image']
    if image.filename == '':
        return render_template('upload_image.html', dog_id=dog_id, error="Nincs kiválasztott kép!")

    files = {'image': (image.filename, image.stream, image.mimetype)}
    image.stream.seek(0)

    resp = requests.post(
        f"{API_URL}/dogs/{dog_id}/upload_image",
        files=files,
        headers=get_auth_headers()
    )
    if resp.status_code not in (200, 201):
        try:
            error = resp.json().get('error', 'Ismeretlen hiba')
        except Exception:
            error = f"Hiba: {resp.status_code} – nem várt válasz."
        return render_template('upload_image.html', dog_id=dog_id, error=error)
    return redirect(url_for('index'))

# ----------------------------------------
# Alkalmazás indítása
# ----------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)