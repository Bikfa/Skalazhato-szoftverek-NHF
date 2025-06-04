from models import db, Owner, Dog, HealthRecord

class OwnerService:
    @staticmethod
    def create(data):
        owner = Owner(
            name=data['name'],
            email=data['email'],
            password=data['password']
        )
        db.session.add(owner)
        db.session.commit()
        return owner

    @staticmethod
    def get(owner_id):
        return Owner.query.get(owner_id)

    @staticmethod
    def update(owner_id, data):
        owner = Owner.query.get(owner_id)
        if not owner:
            return None
        owner.name = data.get('name', owner.name)
        owner.password = data.get('password', owner.password)
        owner.email = data.get('email', owner.email)
        db.session.commit()
        return owner

    @staticmethod
    def delete(owner_id):
        owner = Owner.query.get(owner_id)
        if not owner:
            return None
        db.session.delete(owner)
        db.session.commit()
        return owner

    @staticmethod
    def get_all():
        return Owner.query.all()

class DogService:
    @staticmethod
    def create(data):
        if not Owner.query.get(data['owner_id']):
            return None
        dog = Dog(
            name=data['name'],
            breed=data['breed'],
            color=data['color'],
            gender=data['gender'],
            health_record=data.get('health_record', ''),
            owner_id=data['owner_id']
        )
        db.session.add(dog)
        db.session.commit()
        return dog

    @staticmethod
    def get(dog_id):
        return Dog.query.get(dog_id)

    @staticmethod
    def update(dog_id, data):
        dog = Dog.query.get(dog_id)
        if not dog:
            return None
        dog.name = data.get('name', dog.name)
        dog.breed = data.get('breed', dog.breed)
        dog.color = data.get('color', dog.color)
        dog.gender = data.get('gender', dog.gender)
        dog.health_record = data.get('health_record', dog.health_record)
        db.session.commit()
        return dog

    @staticmethod
    def delete(dog_id):
        dog = Dog.query.get(dog_id)
        if not dog:
            return None
        db.session.delete(dog)
        db.session.commit()
        return dog

class HealthRecordService:
    @staticmethod
    def create(dog_id, data):
        if not Dog.query.get(dog_id):
            return None
        record = HealthRecord(
            dog_id=dog_id,
            type=data['type'],
            description=data['description']
        )
        db.session.add(record)
        db.session.commit()
        return record

    @staticmethod
    def get(record_id):
        return HealthRecord.query.get(record_id)

    @staticmethod
    def get_all_by_dog(dog_id):
        return HealthRecord.query.filter_by(dog_id=dog_id).all()

    @staticmethod
    def update(record_id, data):
        record = HealthRecord.query.get(record_id)
        if not record:
            return None
        record.type = data.get('type', record.type)
        record.description = data.get('description', record.description)
        db.session.commit()
        return record

    @staticmethod
    def delete(record_id):
        record = HealthRecord.query.get(record_id)
        if not record:
            return None
        db.session.delete(record)
        db.session.commit()
        return record
