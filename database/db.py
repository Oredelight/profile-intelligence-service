from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

db_url = os.getenv("DATABASE_URL")

engine = create_engine(db_url, echo=True)

Base = declarative_base()

SessionLocal = sessionmaker(bind= engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()