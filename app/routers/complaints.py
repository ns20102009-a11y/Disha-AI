from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app import crud, schemas, models
from app.services.email_service import send_complaint_email


router = APIRouter(
    prefix="/api/complaints",
    tags=["Complaints"]
)


@router.post("/", response_model=schemas.ComplaintResponse)
def submit_complaint(
    complaint_in: schemas.ComplaintCreate,
    db: Session = Depends(get_db)
):
    complaint = crud.create_complaint(db, complaint_in)

    # Send email after complaint is successfully saved in database.
    # If email fails, complaint will still remain saved.
    send_complaint_email(complaint)

    return complaint


@router.get("/", response_model=List[schemas.ComplaintResponse])
def get_all_complaints(
    db: Session = Depends(get_db)
):
    return crud.get_complaints(db)


@router.patch("/{complaint_id}/status")
def update_complaint_status(
    complaint_id: str,
    status: str,
    admin_notes: str = "",
    db: Session = Depends(get_db)
):
    comp = (
        db.query(models.Complaint)
        .filter(
            models.Complaint.complaint_id == complaint_id
        )
        .first()
    )

    if not comp:
        raise HTTPException(
            status_code=404,
            detail="Complaint not found"
        )

    comp.status = status

    if admin_notes:
        comp.admin_notes = admin_notes

    db.commit()
    db.refresh(comp)

    return {
        "message": "Complaint status updated successfully",
        "complaint_id": comp.complaint_id,
        "status": comp.status,
        "admin_notes": comp.admin_notes
    }
