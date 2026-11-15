from fastapi import FastAPI

app = FastAPI(title="Rent a Car API")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}