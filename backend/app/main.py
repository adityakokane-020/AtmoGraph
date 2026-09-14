from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import verify_connection
from .routes import router


app = FastAPI(
    title="AtmoGraph API",
    version="1.0.0",
    description="Backend API for AtmoGraph Supply Chain Ripple Effect Predictor"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {
        "message": "Welcome to AtmoGraph API",
        "status": "Running"
    }


@app.get("/health")
def health():
    return {
        "status": "OK"
    }


app.include_router(router)

verify_connection()