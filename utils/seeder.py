import json
import os
from datetime import datetime, timezone
from uuid6 import uuid7
from database.db import SessionLocal
from database.model import Profile


def load_seed_profiles():
    """
    Load seed profiles from seed_profiles.json in the root directory.
    Handles deduplication and idempotent seeding.
    
    Returns: dict with created_count, skipped_count, error_count
    """
    # Get the root directory path
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    seed_file = os.path.join(root_dir, "seed_profiles.json")

    if not os.path.exists(seed_file):
        print(f"Seed file not found: {seed_file}")
        return {"created_count": 0, "skipped_count": 0, "error_count": 0}

    try:
        with open(seed_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading seed file: {e}")
        return {"created_count": 0, "skipped_count": 0, "error_count": 1}

    profiles = data.get("profiles", [])
    if not profiles:
        print("No profiles found in seed file")
        return {"created_count": 0, "skipped_count": 0, "error_count": 0}

    db = SessionLocal()
    created_count = 0
    skipped_count = 0
    error_count = 0

    try:
        for profile_data in profiles:
            try:
                # Validate required fields
                required_fields = [
                    "name", "gender", "gender_probability", "age", "age_group",
                    "country_id", "country_name", "country_probability"
                ]

                for field in required_fields:
                    if field not in profile_data:
                        print(f"Skipping profile - missing field '{field}': {profile_data.get('name', 'Unknown')}")
                        error_count += 1
                        continue

                # Normalize name (lowercase for comparison)
                name = profile_data["name"].strip().lower()

                # Check if profile already exists
                existing = db.query(Profile).filter(Profile.name == name).first()
                if existing:
                    skipped_count += 1
                    continue

                # Create new profile
                profile = Profile(
                    id=str(uuid7()),
                    name=name,
                    gender=str(profile_data["gender"]).strip().lower(),
                    gender_probability=float(profile_data["gender_probability"]),
                    age=int(profile_data["age"]),
                    age_group=str(profile_data["age_group"]).strip().lower(),
                    country_id=str(profile_data["country_id"]).strip().upper(),
                    country_name=str(profile_data["country_name"]).strip(),
                    country_probability=float(profile_data["country_probability"]),
                    created_at=datetime.now(timezone.utc)
                )

                db.add(profile)
                created_count += 1

            except Exception as e:
                print(f"Error processing profile: {e}")
                error_count += 1
                continue

        # Commit all at once for better performance
        db.commit()
        print(f"Seeding completed - Created: {created_count}, Skipped: {skipped_count}, Errors: {error_count}")

    except Exception as e:
        print(f"Error during seeding: {e}")
        db.rollback()
        error_count += len(profiles) - skipped_count - created_count

    finally:
        db.close()

    return {
        "created_count": created_count,
        "skipped_count": skipped_count,
        "error_count": error_count
    }
