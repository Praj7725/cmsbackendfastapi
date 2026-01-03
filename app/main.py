from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.admin.colleges import router as college_router
from app.core.database import Base, engine

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="College CMS Backend")

# =========================
# CORS CONFIGURATION
# =========================
origins = [
    "http://localhost:8080",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],         # GET, POST, PUT, PATCH, DELETE
    allow_headers=["*"],         # Authorization, Content-Type, etc
)

# Routes
app.include_router(college_router)
