from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
from app.services.crypto_service import sign_certificate_payload

router = APIRouter(prefix="/api/demo", tags=["Demo Scenarios"])

@router.post("/scenario/compliant")
def set_compliant_scenario(db: Session = Depends(get_db)):
    """
    Scenario 1: Reset first certificate to fully valid and compliant (Green Badge).
    """
    cert = db.query(models.Certificate).first()
    if cert:
        cert.is_active = True
        cert.issue_date = datetime.utcnow() - timedelta(days=60)
        cert.expiry_date = datetime.utcnow() + timedelta(days=305)
        cert.instrument.status = "VERIFIED"
        
        insp = cert.inspection
        inspector = insp.inspector if insp else None
        cert_payload = {
            "certificate_number": cert.certificate_number,
            "instrument_serial": cert.instrument.serial_number,
            "brand_make": cert.instrument.brand_make,
            "shop_name": cert.instrument.shop_name,
            "inspector_badge": inspector.badge_number if inspector else "LMO-DL-07",
            "issue_date": cert.issue_date.strftime("%Y-%m-%d"),
            "expiry_date": cert.expiry_date.strftime("%Y-%m-%d"),
        }
        data_hash, signature = sign_certificate_payload(cert_payload)
        cert.data_hash = data_hash
        cert.cryptographic_signature = signature
        
        db.commit()
        return {"scenario": "COMPLIANT_SCALE", "badge": "GREEN", "cert_number": cert.certificate_number}
    raise HTTPException(status_code=404, detail="No certificate found")

@router.post("/scenario/expired")
def set_expired_scenario(db: Session = Depends(get_db)):
    """
    Scenario 2: Set first certificate to EXPIRED (Red Badge) to show expiry warning.
    """
    cert = db.query(models.Certificate).first()
    if cert:
        cert.is_active = False
        cert.issue_date = datetime.utcnow() - timedelta(days=400)
        cert.expiry_date = datetime.utcnow() - timedelta(days=35)
        cert.instrument.status = "EXPIRED"
        db.commit()
        return {"scenario": "EXPIRED_SCALE", "badge": "RED", "cert_number": cert.certificate_number}
    raise HTTPException(status_code=404, detail="No certificate found")

@router.post("/scenario/fraud")
def set_fraud_scenario(db: Session = Depends(get_db)):
    """
    Scenario 3: Simulate high-risk fraud report with broken seal alert.
    """
    cert = db.query(models.Certificate).first()
    if cert:
        cert.instrument.status = "SUSPECTED_TAMPERED"
        db.commit()
        return {"scenario": "FRAUD_SUSPECTED", "badge": "CRITICAL_ALERT", "cert_number": cert.certificate_number}
    raise HTTPException(status_code=404, detail="No certificate found")
