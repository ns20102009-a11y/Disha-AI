from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app import crud, schemas
from app.services.crypto_service import verify_certificate_signature
from app.services.pdf_service import generate_certificate_pdf

router = APIRouter(prefix="/api/certificates", tags=["Certificates"])

@router.get("/{cert_number}")
def get_certificate_details(cert_number: str, db: Session = Depends(get_db)):
    cert = crud.get_certificate_by_number(db, cert_number)
    if not cert:
        raise HTTPException(status_code=404, detail="Certificate not found or unverified")
    
    inst = cert.instrument
    insp = cert.inspection
    inspector = insp.inspector if insp else None
    
    return {
        "certificate_number": cert.certificate_number,
        "issue_date": cert.issue_date.strftime("%d-%b-%Y"),
        "expiry_date": cert.expiry_date.strftime("%d-%b-%Y"),
        "is_active": cert.is_active,
        "qr_code_url": cert.qr_code_filename,
        "data_hash": cert.data_hash,
        "cryptographic_signature": cert.cryptographic_signature,
        "instrument": {
            "id": inst.id,
            "uid": inst.instrument_uid,
            "shop_name": inst.shop_name,
            "shop_address": inst.shop_address,
            "district": inst.district,
            "state": inst.state,
            "type": inst.instrument_type,
            "brand": inst.brand_make,
            "model_approval_no": inst.model_approval_number,
            "serial_number": inst.serial_number,
            "max_capacity": inst.max_capacity,
            "accuracy_class": inst.accuracy_class
        },
        "inspector": {
            "name": inspector.full_name if inspector else "N/A",
            "badge": inspector.badge_number if inspector else "N/A",
            "inspection_date": insp.inspection_date.strftime("%d-%b-%Y %H:%M UTC") if insp else "N/A",
            "distance_verified_meters": insp.distance_from_shop_meters if insp else 0.0
        }
    }

@router.get("/{cert_number}/verify-tamper")
def verify_tamper_proofing(cert_number: str, db: Session = Depends(get_db)):
    """
    Demonstrates cryptographic tamper-proof validation live for judges.
    """
    cert = crud.get_certificate_by_number(db, cert_number)
    if not cert:
        raise HTTPException(status_code=404, detail="Certificate not found")
    
    inst = cert.instrument
    insp = cert.inspection
    inspector = insp.inspector if insp else None

    payload = {
        "certificate_number": cert.certificate_number,
        "instrument_serial": inst.serial_number,
        "brand_make": inst.brand_make,
        "shop_name": inst.shop_name,
        "inspector_badge": inspector.badge_number if inspector else "LMO-HQ-01",
        "issue_date": cert.issue_date.strftime("%Y-%m-%d"),
        "expiry_date": cert.expiry_date.strftime("%Y-%m-%d"),
    }

    is_valid = verify_certificate_signature(payload, cert.cryptographic_signature)

    return {
        "certificate_number": cert.certificate_number,
        "is_cryptographically_valid": is_valid,
        "algorithm": "HMAC-SHA256 with Legal Metrology Authority Private Key",
        "data_hash": cert.data_hash,
        "signature": cert.cryptographic_signature,
        "audit_verdict": "AUTHENTIC - NO TAMPERING DETECTED" if is_valid else "ALERT: TAMPERED CERTIFICATE"
    }

@router.get("/{cert_number}/download-pdf")
def download_certificate_pdf(cert_number: str, db: Session = Depends(get_db)):
    """
    Downloads an authentic, tamper-evident Form-VIII Certificate PDF.
    """
    cert = crud.get_certificate_by_number(db, cert_number)
    if not cert:
        raise HTTPException(status_code=404, detail="Certificate not found")
    
    pdf_buffer = generate_certificate_pdf(cert)
    filename = f"Certificate_{cert_number.replace('-', '_')}.pdf"
    
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
