
from fastapi import FastAPI

from app.routers import companies, contacts

app = FastAPI(title="ClientOS AI API")


@app.get("/health")
def health_check():
    return {"status": "ok"}


app.include_router(companies.router)
app.include_router(contacts.router)
