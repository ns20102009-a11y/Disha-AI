from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.ai_vigilance_service import run_ai_vigilance_audit

router = APIRouter(prefix="/api/vigilance", tags=["AI Vigilance & Fraud Detection"])

@router.get("/audit")
def get_vigilance_audit(db: Session = Depends(get_db)):
    """
    Runs automated AI vigilance checks detecting impossible velocity anomalies,
    ghost inspections, and consumer short-weighing clusters.
    """
    return run_ai_vigilance_audit(db)

@router.post("/order-raid/{instrument_uid}")
def order_vigilance_raid(instrument_uid: str, db: Session = Depends(get_db)):
    """
    Authorizes an emergency flying squad inspection raid for a high-risk scale.
    """
    return {
        "status": "RAID_AUTHORIZED",
        "instrument_uid": instrument_uid,
        "enforcement_team": "Central Vigilance Flying Squad - Team Bravo",
        "directive": "Immediate on-site surprise inspection with certified Class M1 standards under Section 15 of Legal Metrology Act, 2009."
    }
