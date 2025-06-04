from .owners import owners_bp
from .dogs import dogs_bp
from .records import records_bp
from .upload import upload_bp

def register_routes(app):
    app.register_blueprint(owners_bp)
    app.register_blueprint(dogs_bp)
    app.register_blueprint(records_bp)
    app.register_blueprint(upload_bp)
