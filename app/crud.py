import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app import models, schemas
from app.config import STATUTORY_FEES, GEOFENCE_MAX_DISTANCE_METERS
from app.services.geofence_service import is_within_geofence
from app.services.crypto_service import sign_certificate_payload, generate_qr_code

# USERS
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_users_by_role(db: Session, role: str):
    return db.query(models.User).filter(models.User.role == role).all()

def create_user(db: Session, user_data: dict):
    user = models.User(**user_data)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

# INSTRUMENTS
def get_instruments(db: Session, owner_id: int = None, status: str = None):
    query = db.query(models.Instrument)
    if owner_id:
        query = query.filter(models.Instrument.owner_id == owner_id)
    if status:
        query = query.filter(models.Instrument.status == status)
    return query.order_by(models.Instrument.id.desc()).all()

def get_instrument_by_id(db: Session, instrument_id: int):
    return db.query(models.Instrument).filter(models.Instrument.id == instrument_id).first()

def get_instrument_by_serial(db: Session, serial_no: str):
    return db.query(models.Instrument).filter(models.Instrument.serial_number == serial_no).first()

def create_instrument(db: Session, inst_in: schemas.InstrumentCreate):
    # Calculate statutory fee based on type
    fee_info = STATUTORY_FEES.get(inst_in.instrument_type, {'fee': 200.0})
    statutory_fee = fee_info['fee']
    
    uid = f"INST-2026-{random.randint(10000, 99999)}"
    
    instrument = models.Instrument(
        instrument_uid=uid,
        owner_id=inst_in.owner_id,
        shop_name=inst_in.shop_name,
        trade_license_no=inst_in.trade_license_no,
        shop_address=inst_in.shop_address,
        district=inst_in.district,
        state=inst_in.state,
        pincode=inst_in.pincode,
        latitude=inst_in.latitude,
        longitude=inst_in.longitude,
        instrument_type=inst_in.instrument_type,
        brand_make=inst_in.brand_make,
        model_approval_number=inst_in.model_approval_number,
        serial_number=inst_in.serial_number,
        max_capacity=inst_in.max_capacity,
        min_capacity=inst_in.min_capacity,
        verification_interval=inst_in.verification_interval,
        accuracy_class=inst_in.accuracy_class or "Class III",
        statutory_fee=statutory_fee,
        scheduled_date=inst_in.scheduled_date or "Today, 10:30 AM - 11:30 AM",
        contact_person=inst_in.contact_person,
        contact_phone=inst_in.contact_phone,
        status="PENDING_VERIFICATION"
    )
    db.add(instrument)
    db.commit()
    db.refresh(instrument)
    return instrument

# INSPECTIONS & CERTIFICATES
def perform_inspection(db: Session, insp_in: schemas.InspectionCreate, base_url: str = "http://127.0.0.1:8000"):
    instrument = get_instrument_by_id(db, insp_in.instrument_id)
    if not instrument:
        raise ValueError("Instrument not found")
    
    inspector = get_user(db, insp_in.inspector_id)
    if not inspector:
        inspector = db.query(models.User).filter(models.User.role == "INSPECTOR").first()
        if not inspector:
            raise ValueError("Inspector not found")
    
    # Geofence check
    is_passed_geo, distance = is_within_geofence(
        instrument.latitude, instrument.longitude,
        insp_in.inspector_latitude, insp_in.inspector_longitude,
        max_distance_meters=GEOFENCE_MAX_DISTANCE_METERS
    )
    
    # Check technical tests
    tests_passed = (
        insp_in.zero_setting_test and
        insp_in.repeatability_test and
        insp_in.eccentricity_corner_test and
        insp_in.max_error_observed <= insp_in.permissible_error_limit
    )

    final_status = "PASSED" if (is_passed_geo and tests_passed) else "FAILED"
    
    # Create Inspection Record
    inspection = models.InspectionRecord(
        instrument_id=instrument.id,
        inspector_id=inspector.id,
        inspection_date=datetime.utcnow(),
        inspector_latitude=insp_in.inspector_latitude,
        inspector_longitude=insp_in.inspector_longitude,
        distance_from_shop_meters=distance,
        is_geofence_passed=is_passed_geo,
        zero_setting_test=insp_in.zero_setting_test,
        repeatability_test=insp_in.repeatability_test,
        eccentricity_corner_test=insp_in.eccentricity_corner_test,
        iot_reading_captured=insp_in.iot_reading_captured,
        max_error_observed=insp_in.max_error_observed,
        permissible_error_limit=insp_in.permissible_error_limit,
        photo_proof_path=insp_in.photo_proof_path,
        inspector_remarks=insp_in.inspector_remarks,
        status=final_status
    )
    db.add(inspection)
    db.commit()
    db.refresh(inspection)

    certificate = None
    if final_status == "PASSED":
        # Generate Certificate
        dist_code = instrument.district[:2].upper() if len(instrument.district) >= 2 else "DL"
        cert_num = f"LM-{dist_code}-2026-{random.randint(100000, 999999)}"
        issue_date = datetime.utcnow()
        expiry_date = issue_date + timedelta(days=365) # 1 year validity
        
        cert_payload = {
            "certificate_number": cert_num,
            "instrument_serial": instrument.serial_number,
            "brand_make": instrument.brand_make,
            "shop_name": instrument.shop_name,
            "inspector_badge": inspector.badge_number or "LMO-HQ-01",
            "issue_date": issue_date.strftime("%Y-%m-%d"),
            "expiry_date": expiry_date.strftime("%Y-%m-%d"),
        }
        
        data_hash, signature = sign_certificate_payload(cert_payload)
        
        # QR Code Generation
        verify_url = f"{base_url}/verify/{cert_num}"
        qr_path = generate_qr_code(cert_num, verify_url)
        
        certificate = models.Certificate(
            certificate_number=cert_num,
            instrument_id=instrument.id,
            inspection_id=inspection.id,
            issue_date=issue_date,
            expiry_date=expiry_date,
            qr_code_filename=qr_path,
            data_hash=data_hash,
            cryptographic_signature=signature,
            is_active=True
        )
        db.add(certificate)
        
        # Update instrument status
        instrument.status = "VERIFIED"
        db.commit()
        db.refresh(certificate)
    else:
        instrument.status = "REJECTED"
        db.commit()

    return inspection, certificate

def get_inspection_history(db: Session, limit: int = 50):
    records = db.query(models.InspectionRecord).order_by(models.InspectionRecord.id.desc()).limit(limit).all()
    results = []
    for r in records:
        inst = r.instrument
        insp = r.inspector
        cert = r.certificate
        results.append({
            "id": r.id,
            "instrument_id": r.instrument_id,
            "inspection_date": r.inspection_date,
            "status": r.status,
            "shop_name": inst.shop_name if inst else "Commercial Establishment",
            "shop_address": inst.shop_address if inst else "",
            "district": inst.district if inst else "",
            "serial_number": inst.serial_number if inst else "",
            "instrument_type": inst.instrument_type if inst else "",
            "brand_make": inst.brand_make if inst else "",
            "max_capacity": inst.max_capacity if inst else "",
            "inspector_name": insp.full_name if insp else "Devendra Kumar Verma",
            "inspector_badge": insp.badge_number if insp else "LMO-DL-07",
            "certificate_number": cert.certificate_number if cert else None,
            "distance_from_shop_meters": r.distance_from_shop_meters,
            "iot_reading_captured": r.iot_reading_captured,
            "max_error_observed": r.max_error_observed,
            "permissible_error_limit": r.permissible_error_limit,
            "photo_proof_path": r.photo_proof_path,
            "inspector_remarks": r.inspector_remarks,
            "created_at": r.created_at
        })
    return results

def get_certificate_by_number(db: Session, cert_number: str):
    return db.query(models.Certificate).filter(models.Certificate.certificate_number == cert_number).first()

# COMPLAINTS
def create_complaint(db: Session, comp_in: schemas.ComplaintCreate):
    cid = f"GRIEV-2026-{random.randint(1000, 9999)}"
    complaint = models.Complaint(
        complaint_id=cid,
        instrument_id=comp_in.instrument_id,
        complainant_name=comp_in.complainant_name,
        complainant_phone=comp_in.complainant_phone,
        complainant_email=comp_in.complainant_email,
        complaint_type=comp_in.complaint_type,
        description=comp_in.description,
        photo_evidence=comp_in.photo_evidence,
        status="OPEN"
    )
    db.add(complaint)
    db.commit()
    db.refresh(complaint)
    return complaint

def get_complaints(db: Session, limit: int = 50):
    return db.query(models.Complaint).order_by(models.Complaint.id.desc()).limit(limit).all()

# ANALYTICS DASHBOARD
def get_dashboard_analytics(db: Session):
    total_instruments = db.query(models.Instrument).count()
    verified_count = db.query(models.Instrument).filter(models.Instrument.status == "VERIFIED").count()
    pending_count = db.query(models.Instrument).filter(models.Instrument.status == "PENDING_VERIFICATION").count()
    rejected_count = db.query(models.Instrument).filter(models.Instrument.status == "REJECTED").count()
    complaints_count = db.query(models.Complaint).filter(models.Complaint.status == "OPEN").count()
    
    compliance_rate = round((verified_count / total_instruments * 100), 1) if total_instruments > 0 else 100.0
    
    recent_inspections = db.query(models.InspectionRecord).order_by(models.InspectionRecord.id.desc()).limit(5).all()
    recent_complaints = db.query(models.Complaint).order_by(models.Complaint.id.desc()).limit(5).all()
    
    return {
        "total_instruments": total_instruments,
        "verified_count": verified_count,
        "pending_count": pending_count,
        "rejected_count": rejected_count,
        "complaints_count": complaints_count,
        "compliance_rate": compliance_rate,
        "recent_inspections": recent_inspections,
        "recent_complaints": recent_complaints
    }
