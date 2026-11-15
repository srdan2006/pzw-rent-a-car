from fastapi import FastAPI

from app.core.errors import register_error_handlers

app = FastAPI(title="Rent a Car API")
register_error_handlers(app)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}