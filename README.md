# Profile Intelligence Service

A FastAPI-based microservice that enriches user profiles with demographic intelligence by aggregating data from multiple public APIs. The service infers gender, age, and nationality from a person's name and stores the results in a PostgreSQL database.

Here is the link to the live: https://profile-intelligence-service-production-6c59.up.railway.app/

## Features

- **Profile Enrichment**: Automatically enrich profiles with demographic data based on name
- **Multi-Source Data Integration**: Aggregates insights from three public APIs:
  - [Genderize.io](https://genderize.io) - Gender prediction
  - [Agify.io](https://agify.io) - Age prediction
  - [Nationalize.io](https://nationalize.io) - Nationality prediction
- **Intelligent Filtering**: Query profiles by gender, country, or age group
- **CORS Support**: Cross-origin requests enabled for frontend integration
- **Error Handling**: Comprehensive error responses with meaningful messages
- **Async Operations**: Non-blocking API calls for improved performance

## Project Structure

```
profile-intelligence-service/
├── main.py                 # FastAPI application setup and middleware
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (DATABASE_URL)
├── README.md              # This file
├── database/
│   ├── db.py              # Database connection and session management
│   ├── model.py           # SQLAlchemy ORM models
│   ├── schemas.py         # Pydantic request/response schemas
│   └── serializer.py      # Profile serialization helpers
├── services/
│   └── function.py        # Business logic and external API calls
└── transport/
    └── routes.py          # API route definitions
```

## Prerequisites

- Python 3.8 or higher
- PostgreSQL 12 or higher (or Supabase PostgreSQL instance)
- pip or poetry for dependency management

## Installation

### 1. Clone the repository
```bash
git clone https://github.com/Oredelight/profile-intelligence-service
cd profile-intelligence-service
```

### 2. Create and activate virtual environment
```bash
python -m venv venv

# On Windows:
.\venv\Scripts\Activate.ps1

# On macOS/Linux:
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
Create or update the `.env` file with your database connection string:

```env
DATABASE_URL=postgresql://username:password@host:port/database
```

**For Supabase Users:**
- If you're using **IPv4 networks**, use the Session Pooler endpoint (port 6543):
  ```env
  DATABASE_URL=postgresql://username:password@host:6543/database
  ```
- For direct connections (IPv6), use port 5432:
  ```env
  DATABASE_URL=postgresql://username:password@host:5432/database
  ```

### 5. Verify Python environment
Ensure `python-dotenv` is installed (it's in requirements.txt), which loads environment variables from `.env` file automatically.

## Running the Application

### Development Mode
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

### Interactive API Documentation
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## API Endpoints

All endpoints are prefixed with `/api/profiles`

### CREATE Profile
**Endpoint**: `POST /api/profiles`

Enriches a profile with demographic data based on the provided name.

**Request**:
```json
{
  "name": "john"
}
```

**Responses**:

Success (New Profile):
```json
{
  "status": "success",
  "data": {
    "id": "01a23b45c6d789e0f1g2h3i4j5k6l7m8",
    "name": "john",
    "gender": "male",
    "gender_probability": 0.99,
    "sample_size": 12500,
    "age": 28,
    "age_group": "adult",
    "country_id": "US",
    "country_probability": 0.25,
    "created_at": "2024-04-16T10:30:45Z"
  }
}
```

Duplicate (Profile Already Exists):
```json
{
  "status": "success",
  "message": "Profile already exists",
  "data": { ... }
}
```

Status Codes:
- `200`: Profile created or already exists
- `400`: Name is required
- `422`: Name must be alphabetic characters only
- `502`: One of the external APIs returned an invalid response

---

### GET Profile by ID
**Endpoint**: `GET /api/profiles/{id}`

Retrieve a specific profile by its UUID.

**Response**:
```json
{
  "status": "success",
  "data": {
    "id": "01a23b45c6d789e0f1g2h3i4j5k6l7m8",
    "name": "john",
    "gender": "male",
    "gender_probability": 0.99,
    "sample_size": 12500,
    "age": 28,
    "age_group": "adult",
    "country_id": "US",
    "country_probability": 0.25,
    "created_at": "2024-04-16T10:30:45Z"
  }
}
```

Status Codes:
- `200`: Profile found
- `404`: Profile not found

---

### LIST Profiles (with Filters)
**Endpoint**: `GET /api/profiles`

Retrieve all profiles with optional filtering.

**Query Parameters**:
- `gender` (optional): Filter by gender ("male", "female")
- `country_id` (optional): Filter by country code ("US", "GB", etc.)
- `age_group` (optional): Filter by age group ("child", "teenager", "adult", "senior")

**Examples**:
```
GET /api/profiles?gender=male
GET /api/profiles?country_id=US
GET /api/profiles?age_group=adult
GET /api/profiles?gender=male&country_id=US&age_group=adult
```

**Response**:
```json
{
  "status": "success",
  "count": 2,
  "data": [
    {
      "id": "01a23b45c6d789e0f1g2h3i4j5k6l7m8",
      "name": "john",
      "gender": "male",
      "age": 28,
      "age_group": "adult",
      "country_id": "US"
    },
    {
      "id": "02b34c56d7e890f1a2g3h4i5j6k7l8m9",
      "name": "james",
      "gender": "male",
      "age": 35,
      "age_group": "adult",
      "country_id": "US"
    }
  ]
}
```

Status Codes:
- `200`: Success (may return empty array)

---

### DELETE Profile
**Endpoint**: `DELETE /api/profiles/{id}`

Remove a profile from the database.

**Response**:
- `204`: Profile deleted successfully (no content)

Status Codes:
- `204`: Profile deleted
- `404`: Profile not found

---

## Database Schema

### Profiles Table

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | String | PK, Indexed | Unique identifier (UUIDv7) |
| `name` | String | UNIQUE, NOT NULL | Person's name (lowercase) |
| `gender` | String | | Predicted gender ("male"/"female") |
| `gender_probability` | Float | | Confidence score (0.0-1.0) |
| `sample_size` | Integer | | Number of records used for prediction |
| `age` | Integer | | Predicted age in years |
| `age_group` | String | | Age category ("child", "teenager", "adult", "senior") |
| `country_id` | String | | ISO 3166-1 alpha-2 country code |
| `country_probability` | Float | | Country prediction confidence (0.0-1.0) |
| `created_at` | String | | ISO 8601 timestamp (UTC) |

## Age Group Classification

- **Child**: ≤ 12 years
- **Teenager**: 13-19 years
- **Adult**: 20-59 years
- **Senior**: ≥ 60 years

## Error Handling

The API returns consistent error responses:

```json
{
  "status": "error",
  "message": "Error description"
}
```

### Common Error Scenarios

| Error | Status | Cause |
|-------|--------|-------|
| Name is required | 400 | Empty or whitespace-only name provided |
| Name must be a string | 422 | Name contains non-alphabetic characters |
| Profile not found | 404 | Requested profile ID doesn't exist |
| Genderize returned an invalid response | 502 | External API error or no gender data for name |
| Agify returned an invalid response | 502 | External API error or no age data for name |
| Nationalize returned an invalid response | 502 | External API error or no country data for name |

## Configuration

### Middleware
- **CORS**: Allows all origins, methods, and headers for development
  - Modify in `main.py` for production use

### Database
- **SQLAlchemy**: ORM for database operations
- **Connection Pooling**: Managed by SQLAlchemy
- **Echo Mode**: SQL queries logged to console (enabled in `db.py`)

### Environment
- `.env` file is automatically loaded via `python-dotenv`

## Development Notes

### Adding New Fields
1. Update the `Profile` model in `database/model.py`
2. Update serializer functions in `database/serializer.py`
3. Create a new database migration (if using Alembic)

### Rate Limiting (Not Implemented)
The external APIs have rate limits. Consider implementing:
- Request throttling
- Caching of results
- Rate limit headers in responses

### Performance Considerations
- Async/await is used for concurrent API calls
- Database indexes on commonly filtered columns (id, name, country_id, gender, age_group)
- Consider adding pagination for large datasets

## External APIs Used

1. **Genderize.io**
   - Endpoint: `https://api.genderize.io?name={name}`
   - Returns: Predicted gender and probability

2. **Agify.io**
   - Endpoint: `https://api.agify.io?name={name}`
   - Returns: Predicted age

3. **Nationalize.io**
   - Endpoint: `https://api.nationalize.io?name={name}`
   - Returns: Predicted country and probability

