import os
from pathlib import Path
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.config import SYSTEM_NAME, SYSTEM_SUBTITLE, STATIC_DIR, BASE_DIR
from app.database import engine, Base, get_db
from app.seed_data import seed_database
from app import crud, models
from app.routers import instruments, inspections, certificates, complaints, iot, notifications, vigilance, demo, manufacturers, productguard

# Create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=f"{SYSTEM_NAME} - Legal Metrology Verification System",
    description="Online Verification and Digital Stamping System for Weighing and Measuring Instruments (Department of Consumer Affairs, Government of India)",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Static Files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Templates
templates_dir = BASE_DIR / "app" / "templates"
templates = Jinja2Templates(directory=str(templates_dir))

# Include API Routers
app.include_router(instruments.router)
app.include_router(inspections.router)
app.include_router(certificates.router)
app.include_router(complaints.router)
app.include_router(iot.router)
app.include_router(notifications.router)
app.include_router(vigilance.router)
app.include_router(demo.router)
app.include_router(manufacturers.router)
app.include_router(productguard.router)

# Startup Event: Seed Demo Data
@app.on_event("startup")
def on_startup():
    seed_database()

# FRONTEND WEB PAGES
@app.get("/")
def home_page(request: Request, db: Session = Depends(get_db)):
    first_cert = db.query(models.Certificate).first()
    demo_cert = first_cert.certificate_number if first_cert else "LM-DL-2026-000000"
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "system_name": SYSTEM_NAME,
            "system_subtitle": SYSTEM_SUBTITLE,
            "demo_cert_number": demo_cert
        }
    )

@app.get("/trader")
def trader_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="trader.html",
        context={"system_name": SYSTEM_NAME}
    )

@app.get("/inspector")
def inspector_page(request: Request, inst_id: int = None):
    return templates.TemplateResponse(
        request=request,
        name="inspector.html",
        context={"system_name": SYSTEM_NAME, "initial_inst_id": inst_id}
    )

@app.get("/verify/{cert_number}")
def verify_trust_badge_page(request: Request, cert_number: str):
    return templates.TemplateResponse(
        request=request,
        name="verify_badge.html",
        context={
            "cert_number": cert_number,
            "system_name": SYSTEM_NAME
        }
    )

@app.get("/certificate/{cert_number}")
def official_certificate_page(request: Request, cert_number: str, db: Session = Depends(get_db)):
    cert = crud.get_certificate_by_number(db, cert_number)
    if not cert:
        raise HTTPException(status_code=404, detail="Certificate not found")
    return templates.TemplateResponse(
        request=request,
        name="certificate_view.html",
        context={
            "cert": cert,
            "cert_number": cert_number
        }
    )

@app.get("/sticker/{cert_number}")
def printable_scale_sticker_page(request: Request, cert_number: str, db: Session = Depends(get_db)):
    cert = crud.get_certificate_by_number(db, cert_number)
    if not cert:
        raise HTTPException(status_code=404, detail="Certificate not found")
    return templates.TemplateResponse(
        request=request,
        name="sticker_view.html",
        context={
            "cert": cert,
            "cert_number": cert_number
        }
    )

@app.get("/admin")
def admin_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="admin.html",
        context={"system_name": SYSTEM_NAME}
    )

@app.get("/pitch")
def pitch_deck_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="pitch.html",
        context={"system_name": SYSTEM_NAME}
    )

@app.get("/manufacturer")
def manufacturer_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="manufacturer.html",
        context={"system_name": SYSTEM_NAME}
    )

@app.get("/grievances")
def grievance_tracker_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="grievance_tracker.html",
        context={"system_name": SYSTEM_NAME}
    )

@app.get("/scale-simulator")
def scale_simulator_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="scale_simulator.html",
        context={"system_name": SYSTEM_NAME}
    )

@app.get("/productguard")
def productguard_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="productguard.html",
        context={"system_name": "ProductGuard AI"}
    )

@app.get("/api/analytics")
def get_analytics(db: Session = Depends(get_db)):
    return crud.get_dashboard_analytics(db)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
