# backend/app/main.py

from fastapi import FastAPI
from app.api.endpoints import generate as generate_router # Alias to avoid name clash

app = FastAPI(
    title="SchemaGenius API",
    description="API for automatically generating database schemas from various inputs.",
    version="0.1.0"
)

# Include routers
app.include_router(generate_router.router, prefix="/api/v1", tags=["Schema Generation"])

@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to the SchemaGenius API. See /docs for API documentation."}

# To run this application (from backend/ directory):
# uvicorn app.main:app --reload
