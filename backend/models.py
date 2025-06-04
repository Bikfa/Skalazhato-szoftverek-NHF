from datetime import datetime
from extensions import db

class Owner(db.Model):
    __tablename__ = 'owners'
    id       = db.Column(db.Integer,   primary_key=True)
    email    = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    name     = db.Column(db.String(80),   nullable=False)
    dogs     = db.relationship('Dog', backref='owner', lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "password": self.password,
            "dogs": [dog.to_dict() for dog in self.dogs]
        }

class Dog(db.Model):
    __tablename__ = 'dogs'
    id = db.Column(db.Integer, primary_key=True)
    name  = db.Column(db.String(80), nullable=False)
    breed = db.Column(db.String(50), nullable=False)
    color = db.Column(db.String(50), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    image_path = db.Column(db.String(255), nullable=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('owners.id'), nullable=False)

    # Új relationship a HealthRecord-okhoz
    health_records = db.relationship(
        'HealthRecord',
        backref='dog',
        lazy=True,
        cascade="all, delete-orphan",
        order_by="HealthRecord.created_at.desc()"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "breed": self.breed,
            "color": self.color,
            "gender": self.gender,
            "image_path": self.image_path,
            "owner_id": self.owner_id
        }

class HealthRecord(db.Model):
    __tablename__ = 'health_records'
    id = db.Column(db.Integer, primary_key=True)
    dog_id = db.Column(db.Integer, db.ForeignKey('dogs.id'), nullable=False)
    description = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "dog_id": self.dog_id,
            "description": self.description,
            "created_at": self.created_at.isoformat()
        }
