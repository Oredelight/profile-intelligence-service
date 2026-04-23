from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from database.db import engine, Base
from database.model import Profile
from transport import routes
import sys

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom error format (CRITICAL)
@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "message": str(exc.detail)
        }
    )

app.include_router(routes.router)


# Seed command
def seed_database():
    """Seed the database with profiles from seed_profiles.json"""
    from utils.seeder import load_seed_profiles
    result = load_seed_profiles()
    print(f"\nSeeding Result:")
    print(f"  Created: {result['created_count']}")
    print(f"  Skipped (duplicates): {result['skipped_count']}")
    print(f"  Errors: {result['error_count']}")


if __name__ == "__main__":
    # Check if seed command was passed
    if len(sys.argv) > 1 and sys.argv[1] == "seed":
        seed_database()
    else:
        print("Usage: python main.py seed")

