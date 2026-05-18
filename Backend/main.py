from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import guest_router, student_router, admin_router

app = FastAPI(title="University Management System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500", "http://localhost:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(guest_router)
app.include_router(student_router)
app.include_router(admin_router)


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/metadata/genders")
async def get_genders():
    from models import GenderEnum

    return [g.value for g in GenderEnum]
