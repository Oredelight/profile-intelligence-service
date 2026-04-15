from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from sqlalchemy import func
from database.db import get_db
from database.model import Profile
from database.schemas import ProfileCreate
from services.function import fetch_external_data, get_age_group
from database.serializer import serialize_profile, serialize_profile_list
from uuid6 import uuid7
from datetime import datetime, timezone

router = APIRouter(prefix="/api/profiles", tags=["Profiles"])

# POST
@router.post("")
async def create_profile(payload: ProfileCreate, db: Session = Depends(get_db)):
    name = payload.name.strip().lower()

    if not name:
        raise HTTPException(status_code=400, detail="Name is required")
    if not name.isalpha():
        raise HTTPException(status_code=422, detail="Name must be a string")

    existing = db.query(Profile).filter(Profile.name == name).first()
    if existing:
        return {
            "status": "success",
            "message": "Profile already exists",
            "data": serialize_profile(existing)
        }

    try:
        gender_data, age_data, country_data = await fetch_external_data(name)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"{str(e)} returned an invalid response")

    # Validate Genderize
    if gender_data.get("gender") is None or gender_data.get("count") == 0:
        raise HTTPException(status_code=502, detail="Genderize returned an invalid response")

    # Validate Agify
    if age_data.get("age") is None:
        raise HTTPException(status_code=502, detail="Agify returned an invalid response")

    # Validate Nationalize
    if not country_data.get("country"):
        raise HTTPException(status_code=502,detail="Nationalize returned an invalid response")

    top_country = max(country_data["country"], key=lambda x: x["probability"])

    profile = Profile(
        id=str(uuid7()),
        name=name,
        gender=gender_data["gender"],
        gender_probability=gender_data["probability"],
        sample_size=gender_data["count"],
        age=age_data["age"],
        age_group=get_age_group(age_data["age"]),
        country_id=top_country["country_id"],
        country_probability=top_country["probability"],
        created_at=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    )

    db.add(profile)
    db.commit()
    db.refresh(profile)

    return {
        "status": "success",
        "data": serialize_profile(profile)
    }


# GET by ID
@router.get("/{id}")
def get_profile(id: str, db: Session = Depends(get_db)):
    profile = db.query(Profile).filter(Profile.id == id).first()

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    return {
        "status": "success",
        "data": serialize_profile(profile)
    }


# GET list with filters
@router.get("")
def list_profiles(gender: str = None, country_id: str = None, age_group: str = None, db: Session = Depends(get_db)):
    query = db.query(Profile)

    if gender:
        query = query.filter(func.lower(Profile.gender) == gender.lower())

    if country_id:
        query = query.filter(func.lower(Profile.country_id) == country_id.lower())

    if age_group:
        query = query.filter(func.lower(Profile.age_group) == age_group.lower())

    results = query.all()

    data = [serialize_profile_list(p) for p in results]

    return {
        "status": "success",
        "count": len(data),
        "data": data
    }


# DELETE
@router.delete("/{id}")
def delete_profile(id: str, db: Session = Depends(get_db)):
    profile = db.query(Profile).filter(Profile.id == id).first()

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    db.delete(profile)
    db.commit()

    return Response(status_code=204)