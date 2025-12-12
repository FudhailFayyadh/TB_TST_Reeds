# 📚 BC-3 Personalization Context API

[![CI Pipeline](https://github.com/FudhailFayyadh/TB_TST_Reeds/actions/workflows/ci.yml/badge.svg)](https://github.com/FudhailFayyadh/TB_TST_Reeds/actions/workflows/ci.yml)
![Coverage](https://img.shields.io/badge/coverage-98%25-brightgreen)
![Python](https://img.shields.io/badge/python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688)
![License](https://img.shields.io/badge/license-MIT-green)

**Course:** II3160 – Teknologi Sistem Terintegrasi (ITB)  
**Milestone:** 6 – Testing & CI/CD  
**Bounded Context:** Personalization (Core Domain)  
**Student:** 18223121

---

## 🎯 Overview

This project implements the **Personalization Context** for a book recommendation system following **Domain-Driven Design (DDD)** principles. The system manages user reading preferences, reading history, and content filtering.

### Milestone 6 Updates 🧪
- ✅ **TDD with 98% Test Coverage** - 214 comprehensive unit, integration, and API tests
- ✅ **GitHub Actions CI/CD** - Automated testing, linting, and security checks
- ✅ **pytest + pytest-cov** - Test framework with coverage reporting
- ✅ **ruff Linting** - Code quality and style enforcement

### Milestone 5 Updates 🔐
- ✅ **JWT-based Authentication** - Secure token-based authentication
- ✅ **User Registration & Login** - OAuth2 compatible endpoints
- ✅ **Protected API Endpoints** - All profile endpoints require authentication
- ✅ **Authorization** - Users can only access their own profiles

### Core Features
- ✅ User profile management with reading preferences
- ✅ Favorite genre management (max 5 genres)
- ✅ Book rating system (1-5 scale)
- ✅ Content blocking functionality
- ✅ Reading history tracking
- ✅ Profile snapshots (CQRS read model)

### Business Invariants Enforced
1. **Maximum 5 favorite genres** per user
2. **Rating must be between 1-5**
3. **Unique reading history** per (userId, bookId)
4. **Cannot block active books** (books with ratings)

---

## 🏗️ Architecture

### DDD Layered Architecture
```
┌─────────────────────────────────────────┐
│     Interface Layer (REST API)          │
│   FastAPI Controllers + JWT Auth        │
├─────────────────────────────────────────┤
│   Application Layer (Orchestration)     │
│     Services, DTOs, Use Cases           │
├─────────────────────────────────────────┤
│    Domain Layer (Business Logic)        │
│  Aggregates, Entities, Value Objects    │
│        Domain Events, Invariants        │
├─────────────────────────────────────────┤
│  Infrastructure Layer (Technical)       │
│   Repository, In-Memory DB, JWT Auth    │
└─────────────────────────────────────────┘
```

### Domain Model
- **Aggregate Root:** ProfilMinatBaca
- **Entities:** RiwayatBaca
- **Value Objects:** UserId, GenreFavorit, Rating, DaftarBlokir, PreferensiEksplisit
- **Domain Events:** RatingDiberikan, GenreFavoritDiubah, ItemDiblokir
- **Read Model:** SnapshotProfil (CQRS pattern)

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9 or higher
- pip (Python package manager)

### Installation

1. **Clone or navigate to the project directory:**
   ```powershell
   cd c:\Akademik\TB_TST_Reeds
   ```

2. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```powershell
   uvicorn main:app --reload
   ```
   
   Or alternatively:
   ```powershell
   python main.py
   ```

4. **Access the API:**
   - **Swagger UI:** http://localhost:8000/docs
   - **ReDoc:** http://localhost:8000/redoc
   - **Health Check:** http://localhost:8000/health

---

## 🔐 Authentication (Milestone 5)

### Demo Credentials
```
Username: demo_user
Password: demo123
User ID: user_001
```

### Authentication Flow

1. **Login to get JWT token:**
```http
POST /auth/login
Content-Type: application/x-www-form-urlencoded

username=demo_user&password=demo123
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

2. **Use token in requests:**
```http
GET /profile/user_001
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### Auth Endpoints

#### Register User
```http
POST /auth/register
Content-Type: application/json

{
  "username": "new_user",
  "password": "password123"
}
```

#### Login (OAuth2)
```http
POST /auth/login
Content-Type: application/x-www-form-urlencoded

username=demo_user&password=demo123
```

#### Login (JSON)
```http
POST /auth/token
Content-Type: application/json

{
  "username": "demo_user",
  "password": "demo123"
}
```

#### Get Current User
```http
GET /auth/me
Authorization: Bearer <token>
```

---

## 📡 API Endpoints (Protected)

### Profile Management

> ⚠️ **All profile endpoints require JWT authentication**
> Include `Authorization: Bearer <token>` header in all requests

#### Create Profile
```http
POST /profile/{user_id}
Authorization: Bearer <token>
```
Creates a new user profile. Users can only create their own profile.

#### Get Profile
```http
GET /profile/{user_id}
Authorization: Bearer <token>
```
Retrieves user profile details. Users can only view their own profile.

#### Get Snapshot (Read Model)
```http
GET /profile/{user_id}/snapshot
Authorization: Bearer <token>
```
Retrieves optimized profile snapshot with statistics.

### Genre Management

#### Add Favorite Genre
```http
POST /profile/{user_id}/genre
Authorization: Bearer <token>
Content-Type: application/json

{
  "genre": "Fantasy"
}
```
Max 5 genres allowed per user.

### Rating Management

#### Add/Update Rating
```http
POST /profile/{user_id}/rating
Authorization: Bearer <token>
Content-Type: application/json

{
  "book_id": "book-123",
  "rating": 5
}
```
Rating must be between 1-5.

### Content Filtering

#### Block Book
```http
POST /profile/{user_id}/block
Authorization: Bearer <token>
Content-Type: application/json

{
  "book_id": "book-456"
}
```
Cannot block books with existing ratings.

---

## 🧪 Testing

### Automated Test Script

Run the included test script to verify all functionality:

```powershell
python test_api.py
```

This script tests:
- Profile creation
- Genre management
- Rating system
- Book blocking
- All business invariants
- Read model generation

### Manual Testing with cURL

**Create a profile:**
```powershell
curl -X POST "http://localhost:8000/profile/user-001"
```

**Add genres:**
```powershell
curl -X POST "http://localhost:8000/profile/user-001/genre" `
  -H "Content-Type: application/json" `
  -d '{"genre": "Fantasy"}'
```

**Add ratings:**
```powershell
curl -X POST "http://localhost:8000/profile/user-001/rating" `
  -H "Content-Type: application/json" `
  -d '{"book_id": "book-101", "rating": 5}'
```

**Get snapshot:**
```powershell
curl -X GET "http://localhost:8000/profile/user-001/snapshot"
```

---

## 📁 Project Structure

```
TB_TST_Reeds/
├── .github/
│   └── workflows/
│       └── ci.yml               # GitHub Actions CI/CD
├── src/
│   └── personalization/
│       ├── domain/
│       │   ├── aggregates/
│       │   │   └── profil_minat_baca.py
│       │   ├── entities/
│       │   │   └── riwayat_baca.py
│       │   ├── value_objects/
│       │   │   ├── user_id.py
│       │   │   ├── genre_favorit.py
│       │   │   ├── rating.py
│       │   │   ├── daftar_blokir.py
│       │   │   └── preferensi_eksplisit.py
│       │   ├── events/
│       │   │   ├── rating_diberikan.py
│       │   │   ├── genre_favorit_diubah.py
│       │   │   └── item_diblokir.py
│       │   └── read_models/
│       │       └── snapshot_profil.py
│       ├── application/
│       │   ├── services/
│       │   │   └── profil_service.py
│       │   └── dto/
│       │       ├── profile_dto.py
│       │       ├── genre_dto.py
│       │       ├── rating_dto.py
│       │       └── block_dto.py
│       ├── infrastructure/
│       │   ├── auth/
│       │   │   ├── jwt_handler.py
│       │   │   ├── dependencies.py
│       │   │   └── models.py
│       │   ├── repositories/
│       │   │   └── profil_repository.py
│       │   └── in_memory/
│       │       └── in_memory_profil_repository.py
│       └── interface/
│           └── controllers/
│               ├── auth_controller.py
│               └── profile_controller.py
├── tests/
│   ├── conftest.py
│   ├── unit/                    # 165 tests
│   ├── api/                     # 25 tests
│   └── security/                # 24 tests
├── main.py
├── requirements.txt
├── pytest.ini
└── README.md
```

---

## 🎓 Design Decisions

### 1. **Immutable Value Objects**
All value objects use frozen dataclasses to ensure immutability and prevent accidental modifications.

### 2. **Aggregate Root Pattern**
`ProfilMinatBaca` is the only entry point for all modifications, ensuring all invariants are consistently enforced.

### 3. **Repository Pattern**
Abstracts data access through an interface, making it easy to swap the in-memory implementation for a real database.

### 4. **Thin Controllers**
Controllers only handle HTTP concerns (request/response). All business logic resides in the domain layer.

### 5. **CQRS Pattern**
Separate read model (`SnapshotProfil`) optimized for queries, with denormalized data for fast reads.

### 6. **Domain Events**
Events are raised for important domain actions, enabling future event-driven architecture and integration with other bounded contexts.

---

## 📊 Example Usage Flow

```python
# 1. Create profile
POST /profile/user-001

# 2. Add favorite genres
POST /profile/user-001/genre {"genre": "Fantasy"}
POST /profile/user-001/genre {"genre": "Science Fiction"}

# 3. Rate books
POST /profile/user-001/rating {"book_id": "book-101", "rating": 5}
POST /profile/user-001/rating {"book_id": "book-102", "rating": 4}

# 4. Block unwanted content
POST /profile/user-001/block {"book_id": "book-999"}

# 5. Get profile snapshot
GET /profile/user-001/snapshot

# Response:
{
  "user_id": "user-001",
  "genre_favorit": ["Fantasy", "Science Fiction"],
  "jumlah_buku_dibaca": 2,
  "rata_rata_rating": 4.5,
  "blocked_items": ["book-999"],
  "riwayat_baca": [...]
}
```

---

## 🔒 Invariant Enforcement Examples

### 1. Maximum 5 Genres
```python
# After adding 5 genres:
POST /profile/user-001/genre {"genre": "6th Genre"}
# → 400 Bad Request: "Cannot add more than 5 favorite genres"
```

### 2. Rating Must Be 1-5
```python
POST /profile/user-001/rating {"book_id": "book-123", "rating": 6}
# → 422 Unprocessable Entity: Validation error
```

### 3. Cannot Block Active Books
```python
# After rating a book:
POST /profile/user-001/rating {"book_id": "book-123", "rating": 5}
POST /profile/user-001/block {"book_id": "book-123"}
# → 400 Bad Request: "Cannot block active book"
```

---

## 🧪 Testing (Milestone 6)

### Test Coverage: 98% ✅

The project uses **Test-Driven Development (TDD)** with comprehensive test coverage across all layers.

### Test Statistics
| Metric | Value |
|--------|-------|
| **Total Tests** | 214 |
| **Coverage** | 98.14% |
| **Unit Tests** | 165 (97.52% coverage) |
| **API Tests** | 25 |
| **Security Tests** | 24 |

### Test Structure
```
tests/
├── conftest.py                    # Shared fixtures
├── unit/
│   ├── test_value_objects.py      # Rating, GenreFavorit, UserId (28 tests)
│   ├── test_blocklist_preferences.py  # DaftarBlokir, PreferensiEksplisit (21 tests)
│   ├── test_aggregate.py          # ProfilMinatBaca, RiwayatBaca (29 tests)
│   ├── test_service.py            # ProfilService with mocks (17 tests)
│   ├── test_jwt_handler.py        # JWT token & password hashing (20 tests)
│   ├── test_repository.py         # InMemory repository (14 tests)
│   ├── test_dependencies.py       # Auth dependencies (9 tests)
│   └── test_controllers.py        # Controller endpoints (27 tests)
├── api/
│   └── test_endpoints.py          # Full API workflow tests (25 tests)
└── security/
    └── test_auth.py               # JWT security vulnerability tests (24 tests)
```

### Running Tests

```bash
# Run all tests with coverage
pytest

# Run with verbose output
pytest -v --cov=src --cov-report=term-missing

# Run specific test categories
pytest tests/unit/ -v          # Unit tests only (165 tests)
pytest tests/api/ -v           # API tests only (25 tests)
pytest tests/security/ -v      # Security tests only (24 tests)

# Generate HTML coverage report
pytest --cov=src --cov-report=html
# Open htmlcov/index.html in browser
```

### CI/CD Pipeline

The project includes **GitHub Actions** for continuous integration:

| Job | Description | Status |
|-----|-------------|--------|
| **lint** | Code quality checks with ruff | ✅ |
| **test** | Run pytest with 95% coverage threshold | ✅ |
| **security** | Dependency vulnerability checks | ✅ |

Workflow file: [`.github/workflows/ci.yml`](.github/workflows/ci.yml)

```yaml
# Triggers on:
# - Push to main/develop branches
# - Pull requests to main
```

### Test Categories

| Category | Tests | Coverage Focus |
|----------|-------|----------------|
| **Value Objects** | 49 | Immutability, validation, equality |
| **Aggregates** | 29 | Business invariants, domain events |
| **Services** | 17 | Application logic with mocks |
| **Controllers** | 27 | HTTP endpoints, auth |
| **API Integration** | 25 | Full HTTP workflow |
| **Security** | 24 | JWT vulnerabilities, token attacks |
| **Infrastructure** | 43 | Repository, JWT handler, dependencies |

---

## 🚀 Deployment

### Option 1: Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run with hot-reload
uvicorn main:app --reload --port 8000
```

### Option 2: Railway

1. Connect GitHub repo to [Railway](https://railway.app)
2. Set environment variables:
   ```
   PORT=8000
   SECRET_KEY=your-super-secret-key-here
   ```
3. Deploy automatically on push

### Option 3: Docker

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
docker build -t tst-reeds .
docker run -p 8000:8000 tst-reeds
```

---

## 🚧 Future Enhancements

- [x] ~~Authentication & authorization~~ ✅ Milestone 5
- [x] ~~Unit and integration tests~~ ✅ Milestone 6
- [x] ~~CI/CD pipeline~~ ✅ Milestone 6
- [ ] Database persistence (PostgreSQL/MongoDB)
- [ ] Docker containerization
- [ ] Deploy to Railway/Vercel
- [ ] Event handlers and event sourcing
- [ ] Integration with other bounded contexts
- [ ] Recommendation algorithm implementation
- [ ] API rate limiting & caching
- [ ] Monitoring and logging

---

## 📚 Tech Stack

| Category | Technology |
|----------|------------|
| **Framework** | FastAPI 0.104.1 |
| **Language** | Python 3.12 |
| **Authentication** | JWT (python-jose) |
| **Password Hashing** | passlib + bcrypt |
| **Testing** | pytest, pytest-cov, pytest-asyncio |
| **Linting** | ruff |
| **HTTP Client** | httpx 0.27.0 |
| **CI/CD** | GitHub Actions |

---

## 📚 References

- **Domain-Driven Design** by Eric Evans
- **Implementing Domain-Driven Design** by Vaughn Vernon
- **FastAPI Documentation:** https://fastapi.tiangolo.com/
- **Course Materials:** Milestone 2 & 3 documents

---

## 📝 Commit History Highlights

```
feat: Implement Milestone 6 - TDD Testing & CI/CD

Testing:
- Add comprehensive test suite with 214 tests
- Achieve 98% code coverage (target: 95%)
- Unit tests for value objects, aggregates, entities
- Integration tests for services with mocks
- API endpoint tests with authentication
- Security tests for JWT vulnerabilities

CI/CD:
- Add GitHub Actions workflow (.github/workflows/ci.yml)
- Lint job with ruff
- Test job with pytest and coverage threshold
- Security job for dependency checks

Milestone: 6 - Testing & CI/CD
Course: II3160 - Teknologi Sistem Terintegrasi (ITB)
```

---

## 📄 License

MIT License - Feel free to use for educational purposes.

---

## 👨‍💻 Author

**Student ID:** 18223121  
**Course:** II3160 – Teknologi Sistem Terintegrasi  
**Institution:** Institut Teknologi Bandung (ITB)  
**Milestone:** 6 – Testing & CI/CD

