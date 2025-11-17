"""
FastAPI Application - BC-3 Personalization Context
Milestone 4: Implementasi Awal
II3160 – Teknologi Sistem Terintegrasi (ITB)

This application implements the Personalization bounded context
following Domain-Driven Design (DDD) principles.
"""
from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from src.personalization.infrastructure.in_memory import InMemoryProfilMinatBacaRepository
from src.personalization.application.services import ProfilService
from src.personalization.interface.controllers import profile_controller

# Initialize FastAPI application
app = FastAPI(
    title="BC-3 Personalization Context API",
    description="Domain-Driven Design implementation for Reading Interest Profile Management",
    version="1.0.0",
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
app.include_router(profile_controller.router)


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
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
