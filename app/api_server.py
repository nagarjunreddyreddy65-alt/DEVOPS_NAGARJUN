import os
import sys

# Ensure repository root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, payment, reports
from app.database.connection import DatabaseManager

app = FastAPI(
    title="Autonomous DevOps - Enterprise Microservices Platform",
    description="Live REST APIs with real database transactions, JWT authentication, payment processing, and CI/CD optimization",
    version="2.0.0"
)

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount live routers
app.include_router(auth.router)
app.include_router(payment.router)
app.include_router(reports.router)

@app.get("/health", tags=["Health"])
def healthcheck():
    db = DatabaseManager()
    runs = db.get_recent_runs(limit=1)
    return {
        "status": "HEALTHY",
        "service": "Enterprise Microservices Platform",
        "version": "2.0.0",
        "database": "CONNECTED",
        "total_logged_runs": len(db.get_all_runs())
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.api_server:app", host="0.0.0.0", port=8080, reload=True)
