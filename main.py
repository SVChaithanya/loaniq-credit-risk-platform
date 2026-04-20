from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from db import Base, engine
from router import reg, login, refresh, loan, verify, profile

app = FastAPI(
    title="LoanIQ — Credit Risk API",
    description="ML-powered loan risk assessment platform",
    version="2.0.0"
)

# DB init
@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# APIs
app.include_router(reg.router)
app.include_router(verify.router)
app.include_router(login.router)
app.include_router(refresh.router)
app.include_router(profile.router)
app.include_router(loan.router)

# STATIC FRONTEND (IMPORTANT)
app.mount("/", StaticFiles(directory="static", html=True), name="static")

# Health check (NOT root UI)
@app.get("/health")
def health():
    return {"status": "ok"}