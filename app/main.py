from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.admin.colleges import router as colleges_router
from app.api.admin.roles import router as roles_router
from app.api.admin.permissions import router as permissions_router
from app.api.admin.users import router as users_router
from app.api.admin.academic_years import router as academic_years_router
from app.api.admin.education_types import router as education_types_router
from app.api.admin.courses import router as courses_router
from app.api.admin.semesters import router as semesters_router
from app.api.admin.subjects import router as subjects_router
from app.api.auth import router as auth_router
from app.api.admin.faculty import router as faculty
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
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# ROUTES
# =========================
app.include_router(colleges_router)
app.include_router(roles_router)
app.include_router(permissions_router)
app.include_router(users_router)
app.include_router(academic_years_router)
app.include_router(education_types_router)
app.include_router(courses_router)
app.include_router(semesters_router)
app.include_router(subjects_router)
app.include_router(auth_router)
app.include_router(faculty)
