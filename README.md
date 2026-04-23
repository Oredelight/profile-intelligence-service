# Profile Intelligence Service

A FastAPI-based microservice that enriches user profiles with demographic intelligence by aggregating data from multiple public APIs. The service infers gender, age, and nationality from a person's name and stores the results in a PostgreSQL database. It provides advanced filtering, sorting, pagination, and natural language query capabilities for querying large demographic datasets.

Here is the link to the live deployment: https://profile-intelligence-service-production-6c59.up.railway.app/

## Features

- **Profile Enrichment**: Automatically enrich profiles with demographic data based on name
- **Multi-Source Data Integration**: Aggregates insights from three public APIs:
  - [Genderize.io](https://genderize.io) - Gender prediction
  - [Agify.io](https://agify.io) - Age prediction
  - [Nationalize.io](https://nationalize.io) - Nationality prediction
- **Advanced Query Filtering**: Filter profiles by gender, age group, country, and probability thresholds
- **Natural Language Search**: Parse user-friendly queries (e.g., "young females from Nigeria")
- **Sorting & Pagination**: Sort by age, creation date, or gender probability with configurable pagination
- **Profile Management**: Create, retrieve, list, and delete profiles
- **CORS Support**: Cross-origin requests enabled for frontend integration
- **Error Handling**: Comprehensive error responses with meaningful messages
- **Async Operations**: Non-blocking API calls for improved performance
- **Database Indexing**: Optimized queries on gender, country, and age fields
- **Data Seeding**: Load 2026 demographic profiles with deduplication support

## Project Structure

```
profile-intelligence-service/
├── main.py                 # FastAPI application setup and middleware
├── requirements.txt        # Python dependencies
├── seed_profiles.json      # 2026 demographic profiles for seeding
├── .env                    # Environment variables (DATABASE_URL)
├── README.md              # This file
├── database/
│   ├── db.py              # Database connection and session management
│   ├── model.py           # SQLAlchemy ORM models
│   ├── schemas.py         # Pydantic request/response schemas
│   └── serializer.py      # Profile serialization helpers
├── services/
│   └── function.py        # Business logic and external API calls
├── transport/
│   └── routes.py          # API route definitions
└── utils/
    ├── countries.py       # Country code and name mappings
    ├── query_parser.py    # Natural language query parsing
    └── seeder.py          # Database seeding utilities
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

### API Documentation
Once running, access interactive documentation at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Database Seeding

### Load Initial Data (2026 Profiles)
Before seeding, ensure your database is empty or you have backed up existing data.

```bash
python main.py seed
```

**Output example:**
```
Seeding Result:
  Created: 2026
  Skipped (duplicates): 0
  Errors: 0
```

**Re-running seed is safe** — the system automatically detects and skips duplicate profiles by name, so you can run it multiple times without data duplication.

---

## API Endpoints

### 1. Create Profile
**POST** `/api/profiles`

Creates a new profile by fetching demographic data from external APIs.

**Request:**
```json
{
  "name": "John Doe"
}
```

**Response (201 Created or 200 if exists):**
```json
{
  "status": "success",
  "data": {
    "id": "01ARZ3NDEKTSV4RRFFQ69G5FAV",
    "name": "john doe",
    "gender": "male",
    "gender_probability": 0.99,
    "age": 32,
    "age_group": "adult",
    "country_id": "US",
    "country_name": "United States",
    "country_probability": 0.85,
    "created_at": "2026-04-23T10:30:00Z"
  }
}
```

**Error Responses:**
- `400 Bad Request` — Name is required
- `422 Unprocessable Entity` — Invalid name format
- `502 Bad Gateway` — External API error

---

### 2. List Profiles with Advanced Filters
**GET** `/api/profiles`

Retrieve profiles with optional filtering, sorting, and pagination.

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `gender` | string | null | Filter by gender: "male" or "female" |
| `age_group` | string | null | Filter by age group: "child", "teenager", "adult", "senior" |
| `country_id` | string | null | Filter by ISO country code (e.g., "NG", "KE") |
| `min_age` | integer | null | Minimum age (inclusive) |
| `max_age` | integer | null | Maximum age (inclusive) |
| `min_gender_probability` | float | null | Minimum gender confidence score (0.0 - 1.0) |
| `min_country_probability` | float | null | Minimum country confidence score (0.0 - 1.0) |
| `sort_by` | string | "created_at" | Sort field: "age", "created_at", or "gender_probability" |
| `order` | string | "asc" | Sort order: "asc" or "desc" |
| `page` | integer | 1 | Page number (1-indexed) |
| `limit` | integer | 10 | Results per page (max 50) |

**Example Requests:**
```bash
# Get all male profiles from Nigeria aged 25+
curl "http://localhost:8000/api/profiles?gender=male&country_id=NG&min_age=25"

# Get adult females sorted by age descending
curl "http://localhost:8000/api/profiles?gender=female&age_group=adult&sort_by=age&order=desc"

# Paginate through high-confidence profiles
curl "http://localhost:8000/api/profiles?min_gender_probability=0.9&page=2&limit=20"

# Combine multiple filters
curl "http://localhost:8000/api/profiles?gender=male&age_group=teenager&country_id=KE&min_age=15"
```

**Response (200 OK):**
```json
{
  "status": "success",
  "page": 1,
  "limit": 10,
  "total": 512,
  "data": [
    {
      "id": "01ARZ3NDEKTSV4RRFFQ69G5FAV",
      "name": "john doe",
      "gender": "male",
      "age": 28,
      "age_group": "adult",
      "country_id": "NG"
    },
    {
      "id": "01ARZ3NDEKTSV4RRFFQ69G5FAW",
      "name": "jane smith",
      "gender": "female",
      "age": 31,
      "age_group": "adult",
      "country_id": "KE"
    }
  ]
}
```

**Error Responses:**
- `400 Bad Request` — Invalid pagination parameters (page < 1 or limit < 1)
- `422 Unprocessable Entity` — Invalid parameter type or value out of bounds

---

### 3. Natural Language Search
**GET** `/api/profiles/search`

Query profiles using plain English. The system interprets natural language and converts it to filters.

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `q` | string | Yes | Natural language query |
| `page` | integer | No | Page number (default: 1) |
| `limit` | integer | No | Results per page (default: 10, max: 50) |

**Query Language Reference:**

| Example Query | Interpreted Filters | Notes |
|--------------|-------------------|-------|
| `young males` | gender=male, min_age=16, max_age=24 | "young" means ages 16-24 |
| `females above 30` | gender=female, min_age=30 | Supports "above", "over" |
| `people from nigeria` | country_id=NG | Country-aware parsing |
| `adult males from kenya` | gender=male, age_group=adult, country_id=KE | Combined filters |
| `teenagers below 18` | age_group=teenager, max_age=18 | Supports "below", "under" |
| `between 25 and 35` | min_age=25, max_age=35 | Numeric ranges |
| `senior females` | gender=female, age_group=senior | Age groups: child, teenager, adult, senior |
| `children from south africa` | age_group=child, country_id=ZA | Multi-word country support |

**Supported Keywords:**
- **Gender**: male, males, female, females
- **Age Groups**: child, children, teen, teenager, teenagers, adolescent, adult, adults, senior, seniors, elderly, old
- **Age Patterns**: "young" (16-24), "above X", "over X", "below X", "under X", "between X and Y"
- **Countries**: Nigeria, Kenya, Angola, Benin, Ghana, South Africa, Egypt, Morocco, Uganda, Tanzania, Sudan, United States, United Kingdom, etc.

**Example Requests:**
```bash
# Young males from Nigeria
curl "http://localhost:8000/api/profiles/search?q=young+males+from+nigeria"

# Adults aged 30 or older
curl "http://localhost:8000/api/profiles/search?q=adults+above+30"

# Pagination with natural language
curl "http://localhost:8000/api/profiles/search?q=female+teenagers&page=2&limit=25"
```

**Response (200 OK):**
```json
{
  "status": "success",
  "page": 1,
  "limit": 10,
  "total": 145,
  "data": [
    {
      "id": "01ARZ3NDEKTSV4RRFFQ69G5FAV",
      "name": "chioma nwankwo",
      "gender": "female",
      "age": 19,
      "age_group": "teenager",
      "country_id": "NG"
    }
  ]
}
```

**Error Responses:**
- `400 Bad Request` — Missing or empty query parameter "q"
- `400 Bad Request` — Unable to interpret query (no parseable elements found)
- `422 Unprocessable Entity` — Invalid pagination parameters

**Note on Lenient Parsing:** The system uses lenient parsing — if only part of your query can be interpreted, it will apply those filters. For example, "very young xyz males from xyz nigeria" would still parse as "young males from nigeria" by ignoring unparseable words.

---

### 4. Get Profile by ID
**GET** `/api/profiles/{id}`

Retrieve a specific profile by UUID.

**Response (200 OK):**
```json
{
  "status": "success",
  "data": {
    "id": "01ARZ3NDEKTSV4RRFFQ69G5FAV",
    "name": "john doe",
    "gender": "male",
    "gender_probability": 0.99,
    "age": 32,
    "age_group": "adult",
    "country_id": "US",
    "country_name": "United States",
    "country_probability": 0.85,
    "created_at": "2026-04-23T10:30:00Z"
  }
}
```

**Error Responses:**
- `404 Not Found` — Profile not found

---

### 5. Delete Profile
**DELETE** `/api/profiles/{id}`

Delete a profile by UUID.

**Response:**
- `204 No Content` — Profile deleted successfully

**Error Responses:**
- `404 Not Found` — Profile not found

---

## Error Responses

All error responses follow a consistent format:

```json
{
  "status": "error",
  "message": "Descriptive error message"
}
```

### HTTP Status Codes

| Status Code | Scenario | Example |
|-------------|----------|---------|
| 400 | Bad Request — Missing or invalid required parameters | Missing "name" in POST, invalid pagination |
| 422 | Unprocessable Entity — Parameter type or value validation error | Non-integer age, probability > 1.0 |
| 404 | Not Found — Resource doesn't exist | Profile ID not found |
| 502 | Bad Gateway — External API error | Genderize/Agify/Nationalize API failure |

---

## Data Specification

### Profile Schema

| Field | Type | Constraints | Notes |
|-------|------|-----------|-------|
| `id` | UUID v7 | Unique, Primary Key | Auto-generated |
| `name` | VARCHAR | Unique, Required | Stored in lowercase |
| `gender` | VARCHAR | "male" or "female" | From Genderize API |
| `gender_probability` | FLOAT | 0.0 - 1.0 | Confidence score |
| `age` | INTEGER | > 0 | From Agify API |
| `age_group` | VARCHAR | child, teenager, adult, senior | Derived from age |
| `country_id` | VARCHAR(2) | ISO 3166-1 alpha-2 code | From Nationalize API |
| `country_name` | VARCHAR | Full country name | Mapped from country_id |
| `country_probability` | FLOAT | 0.0 - 1.0 | Confidence score |
| `created_at` | TIMESTAMP | UTC ISO 8601 | Auto-generated |

### Age Group Mapping
- **child**: 0-12 years
- **teenager**: 13-19 years
- **adult**: 20-59 years
- **senior**: 60+ years

---

## Performance Considerations

- **Database Indexes**: Indexes on `gender`, `country_id`, and `age` fields for fast filtering
- **Pagination**: Always use pagination (default limit: 10) for large result sets
- **Maximum Limit**: API enforces a maximum limit of 50 records per request to prevent resource exhaustion
- **Query Efficiency**: Combined filters use AND logic for precise targeting

---

## Examples & Use Cases

### Use Case 1: Marketing Segmentation
Find male adults from Nigeria for targeted advertising:
```bash
curl "http://localhost:8000/api/profiles?gender=male&age_group=adult&country_id=NG&limit=50"
```

### Use Case 2: Demographic Research
Query using natural language for quick research:
```bash
curl "http://localhost:8000/api/profiles/search?q=female+teenagers+from+kenya&limit=100"
```

### Use Case 3: High-Confidence Data Only
Filter by probability thresholds for quality assurance:
```bash
curl "http://localhost:8000/api/profiles?min_gender_probability=0.95&min_country_probability=0.9&limit=50"
```

### Use Case 4: Age-Based Analysis
Sort by age and paginate for cohort analysis:
```bash
curl "http://localhost:8000/api/profiles?sort_by=age&order=asc&limit=100&page=1"
```

---

## Troubleshooting

### Database Connection Error
```
Error: psycopg2.OperationalError: could not connect to server
```
**Solution**: Check your `DATABASE_URL` in `.env` file and ensure PostgreSQL is running.

### Seed Command Not Found
**Solution**: Ensure you're running the command from the project root directory and the virtual environment is activated.

### Query Returns Empty Results
- Check that the filter parameters are spelled correctly
- Verify data exists in the database by running a simple unfiltered query
- Use `/docs` endpoint to test parameters interactively

---

## Development & Testing

### Running Tests
```bash
# Add test files in a tests/ directory if needed
pytest tests/
```

### Database Reset
```bash
# To completely reset the database:
# 1. Drop and recreate the database
# 2. Run the application (it will auto-create tables)
# 3. Re-run the seed command
```

---

## License

MIT License - see LICENSE file for details

## Support

For issues, feature requests, or questions, please open an issue on GitHub or contact the development team.


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
  "name": "Grace"
}
```

**Responses**:

Success (New Profile):
```json
{
  "status": "success",
  "data": {
    "id": "019db997-3759-7d7b-8df4-4ac0920b5853",
    "name": "grace",
    "gender": "female",
    "gender_probability": 0.99,
    "age": 61,
    "age_group": "senior",
    "country_id": "NG",
    "country_name": "Nigeria",
    "country_probability": 0.0669367966930942,
    "created_at": "2026-04-23T09:06:28.313547"
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
    "id": "019db997-3759-7d7b-8df4-4ac0920b5853",
    "name": "grace",
    "gender": "female",
    "gender_probability": 0.99,
    "age": 61,
    "age_group": "senior",
    "country_id": "NG",
    "country_name": "Nigeria",
    "country_probability": 0.0669367966930942,
    "created_at": "2026-04-23T09:06:28.313547"
  }
}
```

Status Codes:
- `200`: Profile found
- `404`: Profile not found

---

### LIST Profiles (with Filters, Sorting & Pagination)
**Endpoint**: `GET /api/profiles`

Retrieve all profiles with optional filtering, sorting, and pagination.

**Query Parameters**:
- `gender` (optional): Filter by gender ("male", "female")
- `country_id` (optional): Filter by country code ("US", "GB", etc.)
- `age_group` (optional): Filter by age group ("child", "teenager", "adult", "senior")
- `min_age` (optional): Filter profiles with age >= value
- `max_age` (optional): Filter profiles with age <= value
- `min_gender_probability` (optional): Filter by minimum gender confidence (0.0-1.0)
- `min_country_probability` (optional): Filter by minimum country confidence (0.0-1.0)
- `sort_by` (optional): Sort field ("age", "created_at", "gender_probability"). Default: "created_at"
- `order` (optional): Sort order ("asc", "desc"). Default: "asc"
- `page` (optional): Page number for pagination. Default: 1
- `limit` (optional): Number of results per page (max 50). Default: 10

**Examples**:
```
GET /api/profiles?gender=male&page=1&limit=10
GET /api/profiles?country_id=US&sort_by=age&order=desc
GET /api/profiles?age_group=adult&min_gender_probability=0.9
GET /api/profiles?gender=female&min_age=20&max_age=35&sort_by=created_at
```

**Response**:
```json
{
  "status": "success",
  "page": 1,
  "limit": 10,
  "total": 42,
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

### SEARCH Profiles (Natural Language Query)
**Endpoint**: `GET /api/profiles/search`

Search profiles using natural language queries. The parser automatically extracts filters from your query.

**Query Parameters**:
- `q` (required): Natural language search query
- `page` (optional): Page number for pagination. Default: 1
- `limit` (optional): Number of results per page. Default: 10

**Supported Query Keywords**:
- **Gender**: "male", "female"
- **Age Groups**: "child", "teenager", "adult", "senior"
- **Age Ranges**: "young" (16-24), "above {age}", "below {age}"
- **Countries**: "nigeria", "kenya", "angola"

**Examples**:
```
GET /api/profiles/search?q=young%20females
GET /api/profiles/search?q=male%20above%2030
GET /api/profiles/search?q=adult%20from%20nigeria
GET /api/profiles/search?q=female%20teenager&page=1&limit=20
```

**Response**:
```json
{
  "status": "success",
  "page": 1,
  "limit": 10,
  "total": 15,
  "data": [
    {
      "id": "01a23b45c6d789e0f1g2h3i4j5k6l7m8",
      "name": "alice",
      "gender": "female",
      "age": 22,
      "age_group": "adult",
      "country_id": "US"
    }
  ]
}
```

Status Codes:
- `200`: Search successful (may return empty results)
- `400`: Missing or empty query parameter
- `400`: Unable to interpret query (no matching filters found)

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
| `created_at` | String | 

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

