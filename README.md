# BC-3 Personalization Context - Milestone 5

**Course:** II3160 – Teknologi Sistem Terintegrasi (ITB)  
**Milestone:** 5 – Implementasi Lanjutan (JWT Authentication)  
**Bounded Context:** Personalization (Core Domain)  
**Student:** 18223121

---

## 🎯 Overview

This project implements the **Personalization Context** for a book recommendation system following **Domain-Driven Design (DDD)** principles. The system manages user reading preferences, reading history, and content filtering.

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
c:\Akademik\TB_TST_Reeds\
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
│       │   ├── repositories/
│       │   │   └── profil_repository.py
│       │   └── in_memory/
│       │       └── in_memory_profil_repository.py
│       └── interface/
│           └── controllers/
│               └── profile_controller.py
├── main.py
├── requirements.txt
├── test_api.py
├── .gitignore
├── MILESTONE_4_EXPLANATION.md
└── README.md (this file)
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

## 🚧 Future Enhancements (Next Milestones)

- [ ] Database persistence (PostgreSQL/MongoDB)
- [ ] Event handlers and event sourcing
- [ ] Integration with other bounded contexts
- [ ] Recommendation algorithm implementation
- [ ] Authentication & authorization
- [ ] Unit and integration tests
- [ ] Docker containerization
- [ ] CI/CD pipeline
- [ ] API rate limiting & caching
- [ ] Monitoring and logging

---

## 📚 References

- **Domain-Driven Design** by Eric Evans
- **Implementing Domain-Driven Design** by Vaughn Vernon
- **FastAPI Documentation:** https://fastapi.tiangolo.com/
- **Course Materials:** Milestone 2 & 3 documents

---

## 📝 Git Commit Message

```
feat: Implement BC-3 Personalization Context for Milestone 4

- Add complete DDD folder structure
- Implement ProfilMinatBaca aggregate with all invariants
- Add value objects: UserId, GenreFavorit, Rating, DaftarBlokir, PreferensiEksplisit
- Add RiwayatBaca entity
- Add domain events: RatingDiberikan, GenreFavoritDiubah, ItemDiblokir
- Implement SnapshotProfil read model (CQRS)
- Add repository pattern with in-memory implementation
- Add ProfilService application service
- Add REST API endpoints with FastAPI
- Add Pydantic DTOs for type safety
- Add API documentation and health check endpoint

Business invariants enforced:
- Maximum 5 favorite genres
- Rating must be between 1-5
- Unique reading history per (userId, bookId)
- Cannot block active books

Milestone: 4 - Implementasi Awal
Course: II3160 - Teknologi Sistem Terintegrasi (ITB)
```

---

## 👨‍💻 Author

**Student ID:** 18223121  
**Course:** II3160 – Teknologi Sistem Terintegrasi  
**Institution:** Institut Teknologi Bandung (ITB)  
**Milestone:** 4 – Implementasi Awal

