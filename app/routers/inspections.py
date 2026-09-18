from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app import crud, schemas

router = APIRouter(prefix="/api/inspections", tags=["Inspections"])

@router.get("/pending", response_model=List[schemas.InstrumentResponse])
def get_pending_inspections(db: Session = Depends(get_db)):
    return crud.get_instruments(db, status="PENDING_VERIFICATION")

@router.get("/history", response_model=List[schemas.InspectionHistoryResponse])
def get_inspection_history_list(limit: int = 50, db: Session = Depends(get_db)):
    return crud.get_inspection_history(db, limit=limit)

@router.get("/all", response_model=List[schemas.InstrumentResponse])
def get_all_inspection_instruments(db: Session = Depends(get_db)):
    return crud.get_instruments(db)

@router.post("/", response_model=schemas.InspectionResponse)
def submit_inspection(
    request: Request,
    insp_in: schemas.InspectionCreate,
    db: Session = Depends(get_db)
):
    try:
        base_url = str(request.base_url).rstrip("/")
        inspection, certificate = crud.perform_inspection(db, insp_in, base_url=base_url)
        return inspection
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error processing inspection: {str(e)}")
