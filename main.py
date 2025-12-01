"""
FastAPI Application - BC-3 Personalization Context
Milestone 5: Implementasi Lanjutan - JWT Authentication
II3160 – Teknologi Sistem Terintegrasi (ITB)

This application implements the Personalization bounded context
following Domain-Driven Design (DDD) principles with JWT authentication.
"""
from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from src.personalization.infrastructure.in_memory import InMemoryProfilMinatBacaRepository
from src.personalization.application.services import ProfilService
from src.personalization.interface.controllers import profile_controller
from src.personalization.interface.controllers import auth_controller

# Initialize FastAPI application
app = FastAPI(
    title="BC-3 Personalization Context API",
    description="""
## Domain-Driven Design Implementation for Reading Interest Profile Management

### Milestone 5: JWT Authentication

This API implements the Personalization bounded context with secure JWT authentication.

### Authentication
All profile endpoints require JWT authentication. To access protected endpoints:

1. **Register** a new user at `/auth/register` or use demo credentials
2. **Login** at `/auth/login` to get JWT token
3. Use the token in Authorization header: `Bearer <token>`

### Demo Credentials
- Username: `demo_user`
- Password: `demo123`
- User ID: `user_001`

### Features
- ✅ JWT-based Authentication
- ✅ User Registration & Login
- ✅ Protected Profile Management
- ✅ Domain-Driven Design Architecture
    """,
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Initialize repository (in-memory for Milestone 4)
repository = InMemoryProfilMinatBacaRepository()

# Initialize application service
profil_service = ProfilService(repository)

# Inject service into controller
profile_controller.set_profil_service(profil_service)

# Register routes
app.include_router(auth_controller.router)  # Authentication routes
app.include_router(profile_controller.router)  # Profile routes (protected)


@app.get("/", include_in_schema=False)
async def root():
    """Redirect root to API documentation"""
    return RedirectResponse(url="/docs")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "BC-3 Personalization Context",
        "version": "2.0.0",
        "features": ["JWT Authentication", "DDD Architecture", "Profile Management"]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
