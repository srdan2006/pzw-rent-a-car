from fastapi import FastAPI

from app.core.errors import register_error_handlers
from app.routers import auth, categories, vehicles, reservations

app = FastAPI(title="Rent a Car API")
register_error_handlers(app)

app.include_router(auth.router)
app.include_router(categories.router)
app.include_router(vehicles.router)
app.include_router(reservations.router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}