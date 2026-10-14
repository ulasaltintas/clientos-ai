from fastapi import FastAPI

app = FastAPI(title="ClientOS AI API")

@app.get("/health")
def health_check():
    return {"status": "ok"}