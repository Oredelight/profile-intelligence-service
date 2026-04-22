from database.db import SessionLocal
from database.model import Profile

def seed_profiles(data):
    db = SessionLocal()

    for p in data:
        exists = db.query(Profile).filter(Profile.name == p["name"].lower()).first()
        if exists:
            continue

        db.add(Profile(**p))

    db.commit()
    db.close()