from database.db import Base
from sqlalchemy import Column, DateTime, Index, Integer, String, Float

class Profile(Base):
    __tablename__ = "profiles"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    gender = Column(String)
    gender_probability = Column(Float)
    age = Column(Integer)
    age_group = Column(String)
    country_id = Column(String(2))
    country_name = Column(String)
    country_probability = Column(Float)
    created_at = Column(DateTime, nullable=False)

Index("idx_gender", Profile.gender)
Index("idx_country", Profile.country_id)
Index("idx_age", Profile.age)
