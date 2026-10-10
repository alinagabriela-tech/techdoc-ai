from fastapi import FastAPI

app = FastAPI(
    title="TechDoc AI",
    description="An AI-powered technical documentation assistant.",
    version="0.1.0",
)


@app.get("/")
def home():
    return {
        "message": "Welcome to TechDoc AI!",
        "status": "running",
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}