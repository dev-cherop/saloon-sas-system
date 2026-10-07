
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from  app.api.routes.businesses import router as businesses_router
from  app.api.routes.customers import router as customers_router
from app.api.routes.auth import router as auth_router

from app.db import get_db

app = FastAPI(
    title="Salon Management API",
    version="0.2.0",
    description="Multi-business and multi-branch salon management system",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=False,
    allow_methods=["GET", "POST","PATCH"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(businesses_router)
app.include_router(customers_router)



@app.get("/health", tags=["Health"])
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "salon-management-api",
    }


@app.get("/health/db", tags=["Health"])
def database_health(db: Session = Depends(get_db)) -> dict[str, str]:
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail="Database unavailable",
        ) from exc