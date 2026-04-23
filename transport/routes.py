from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from sqlalchemy import func
from database.db import get_db
from database.model import Profile
from database.schemas import ProfileCreate
from services.function import fetch_external_data, get_age_group
from database.serializer import serialize_profile, serialize_profile_list
from uuid6 import uuid7
from utils.countries import get_country_name
from utils.query_parser import parse_query
from datetime import datetime, timezone
import re

router = APIRouter(prefix="/api/profiles", tags=["Profiles"])


# POST
@router.post("")
async def create_profile(payload: ProfileCreate, db: Session = Depends(get_db)):
    name = payload.name.strip().lower()

    if not name:
        raise HTTPException(status_code=400, detail="Name is required")

    if not re.match(r"^[a-zA-Z][a-zA-Z\s\-']*$", name):
        raise HTTPException(status_code=422, detail="Name must contain only letters, hyphens, spaces, or apostrophes")

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
        raise HTTPException(status_code=502, detail="Nationalize returned an invalid response")

    top_country = max(country_data["country"], key=lambda x: x["probability"])
    country_id = top_country["country_id"]

    gender_probability = gender_data.get("probability")
    if gender_probability is None:
        gender_probability = 0.0

    country_probability = top_country.get("probability")
    if country_probability is None:
        country_probability = 0.0

    profile = Profile(
        id=str(uuid7()),
        name=name,
        gender=gender_data["gender"].strip().lower(),
        gender_probability=gender_probability,
        age=age_data["age"],
        age_group=get_age_group(age_data["age"]),
        country_id=top_country["country_id"],
        country_name=get_country_name(country_id),
        country_probability=country_probability,
        created_at=datetime.now(timezone.utc)
    )

    db.add(profile)
    db.commit()
    db.refresh(profile)

    return {
        "status": "success",
        "data": serialize_profile(profile)
    }


@router.get("/search")
def search_profiles(
    q: str,
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    
    if page < 1 or limit < 1:
        raise HTTPException(status_code=400, detail="Invalid query parameters")

    if limit > 50:
        limit = 50

    if not q or not q.strip():
        raise HTTPException(status_code=400, detail="Invalid query parameters")

    filters = parse_query(q)

    if not filters:
        raise HTTPException(status_code=400, detail="Unable to interpret query")

    query = db.query(Profile)

    if "gender" in filters:
        query = query.filter(Profile.gender == filters["gender"])

    if "age_group" in filters:
        query = query.filter(Profile.age_group == filters["age_group"])

    if "country_id" in filters:
        query = query.filter(Profile.country_id == filters["country_id"])

    if "min_age" in filters:
        query = query.filter(Profile.age >= filters["min_age"])

    if "max_age" in filters:
        query = query.filter(Profile.age <= filters["max_age"])

    total = query.count()

    results = query.offset((page - 1) * limit).limit(limit).all()

    return {
        "status": "success",
        "page": page,
        "limit": limit,
        "total": total,
        "data": [serialize_profile_list(p) for p in results]
    }


@router.get("/{id}")
def get_profile(id: str, db: Session = Depends(get_db)):
    profile = db.query(Profile).filter(Profile.id == id).first()

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    return {
        "status": "success",
        "data": serialize_profile(profile)
    }

@router.get("")
def list_profiles(
    gender: str = None,
    age_group: str = None,
    country_id: str = None,
    min_age: int = None,
    max_age: int = None,
    min_gender_probability: float = None,
    min_country_probability: float = None,
    sort_by: str = "created_at",
    order: str = "asc",
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    if page < 1 or limit < 1:
        raise HTTPException(status_code=400, detail="Invalid query parameters")

    if limit > 50:
        limit = 50

    query = db.query(Profile)

    if gender:
        query = query.filter(Profile.gender.ilike(gender.strip()))

    if age_group:
        query = query.filter(Profile.age_group.ilike(age_group.strip()))

    if country_id:
        query = query.filter(Profile.country_id == country_id.strip().upper())

    if min_age is not None:
        query = query.filter(Profile.age >= min_age)

    if max_age is not None:
        query = query.filter(Profile.age <= max_age)

    if min_gender_probability is not None:
        query = query.filter(Profile.gender_probability >= min_gender_probability)

    if min_country_probability is not None:
        query = query.filter(Profile.country_probability >= min_country_probability)

    base_query = query


    total = base_query.with_entities(func.count()).order_by(None).scalar()


    sort_fields = {
        "age": Profile.age,
        "created_at": Profile.created_at,
        "gender_probability": Profile.gender_probability
    }

    if sort_by not in sort_fields or order not in ["asc", "desc"]:
        return {"status": "error", "message": "Invalid query parameters"}

    sort_column = sort_fields[sort_by]

    if order == "desc":
        base_query = base_query.order_by(sort_column.desc())
    else:
        base_query = base_query.order_by(sort_column.asc())


    offset = (page - 1) * limit

    data = base_query.offset(offset).limit(limit).all()

    return {
        "status": "success",
        "page": page,
        "limit": limit,
        "total": total,
        "data": [serialize_profile_list(p) for p in data]
    }

@router.delete("/{id}")
def delete_profile(id: str, db: Session = Depends(get_db)):
    profile = db.query(Profile).filter(Profile.id == id).first()

    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    db.delete(profile)
    db.commit()

    return Response(status_code=204)