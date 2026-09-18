from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from app.database import get_db
from app import models

router = APIRouter(prefix="/api/manufacturers", tags=["Manufacturers & Model Approvals"])

class ModelApprovalCreate(BaseModel):
    manufacturer_name: str
    brand_name: str
    instrument_type: str
    accuracy_class: str = "Class III"
    max_capacity: str
    rrsl_testing_lab: str = "RRSL Faridabad (Govt of India)"

@router.get("/models")
def get_all_models(db: Session = Depends(get_db)):
    """
    Returns all nationally approved models tested as per OIML recommendations.
    """
    return db.query(models.ModelApproval).order_by(models.ModelApproval.id.desc()).all()

@router.post("/models")
def apply_model_approval(model_in: ModelApprovalCreate, db: Session = Depends(get_db)):
    """
    Manufacturer application for statutory Model Approval and pattern evaluation.
    """
    import random
    year = datetime.utcnow().year
    month = datetime.utcnow().strftime("%m")
    seq = random.randint(100, 999)
    approval_no = f"IND/{month}/{year}/{seq}"

    new_model = models.ModelApproval(
        approval_number=approval_no,
        manufacturer_name=model_in.manufacturer_name,
        brand_name=model_in.brand_name,
        instrument_type=model_in.instrument_type,
        accuracy_class=model_in.accuracy_class,
        max_capacity=model_in.max_capacity,
        rrsl_testing_lab=model_in.rrsl_testing_lab,
        oiml_recommendation="OIML R-76-1:2006",
        validity_years=10,
        status="APPROVED",
        issue_date=datetime.utcnow()
    )
    db.add(new_model)
    db.commit()
    db.refresh(new_model)
    return new_model

@router.get("/verify-model/{approval_number:path}")
def verify_model_approval(approval_number: str, db: Session = Depends(get_db)):
    """
    Public check: Verifies if a scale model approval number is authentic.
    """
    model = db.query(models.ModelApproval).filter(
        models.ModelApproval.approval_number == approval_number
    ).first()
    if not model:
        raise HTTPException(status_code=404, detail="Model Approval Number not found or counterfeit")
    return {
        "is_valid": True,
        "approval_number": model.approval_number,
        "manufacturer": model.manufacturer_name,
        "brand": model.brand_name,
        "instrument_type": model.instrument_type,
        "rrsl_lab": model.rrsl_testing_lab,
        "oiml_standard": model.oiml_recommendation,
        "status": model.status
    }
