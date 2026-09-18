from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app import crud, schemas

router = APIRouter(prefix="/api/instruments", tags=["Instruments"])

@router.get("/", response_model=List[schemas.InstrumentResponse])
def list_instruments(
    owner_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    return crud.get_instruments(db, owner_id=owner_id, status=status)

@router.post("/", response_model=schemas.InstrumentResponse)
def register_instrument(
    instrument_in: schemas.InstrumentCreate,
    db: Session = Depends(get_db)
):
    # Check if serial number already exists
    existing = crud.get_instrument_by_serial(db, instrument_in.serial_number)
    if existing:
        raise HTTPException(status_code=400, detail="Instrument with this Serial Number already registered")
    
    return crud.create_instrument(db, instrument_in)

@router.get("/{instrument_id}", response_model=schemas.InstrumentResponse)
def get_instrument(instrument_id: int, db: Session = Depends(get_db)):
    inst = crud.get_instrument_by_id(db, instrument_id)
    if not inst:
        raise HTTPException(status_code=404, detail="Instrument not found")
    return inst
