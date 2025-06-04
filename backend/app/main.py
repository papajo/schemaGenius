from fastapi import FastAPI

app = FastAPI(title="SchemaGenius API")

@app.get("/")
async def root():
    return {"message": "Welcome to SchemaGenius API"}

# Further endpoints will be added in api/
# Example: from .api import users_router
# app.include_router(users_router, prefix="/users", tags=["users"])
