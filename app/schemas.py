from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# USER SCHEMAS
class UserBase(BaseModel):
    username: str
    full_name: str
    email: str
    phone: str
    role: str
    badge_number: Optional[str] = None
    jurisdiction_district: Optional[str] = None
    jurisdiction_state: Optional[str] = None

class UserResponse(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# INSTRUMENT SCHEMAS
class InstrumentCreate(BaseModel):
    owner_id: int
    shop_name: str
    trade_license_no: str
    shop_address: str
    district: str
    state: str
    pincode: str
    latitude: float
    longitude: float
    instrument_type: str
    brand_make: str
    model_approval_number: str
    serial_number: str
    max_capacity: str
    min_capacity: Optional[str] = "100 g"
    verification_interval: Optional[str] = "12 Months"
    accuracy_class: Optional[str] = "Class III"
    scheduled_date: Optional[str] = None
    contact_person: Optional[str] = None
    contact_phone: Optional[str] = None

class InstrumentResponse(BaseModel):
    id: int
    instrument_uid: str
    owner_id: int
    shop_name: str
    trade_license_no: str
    shop_address: str
    district: str
    state: str
    pincode: str
    latitude: float
    longitude: float
    instrument_type: str
    brand_make: str
    model_approval_number: str
    serial_number: str
    max_capacity: str
    min_capacity: Optional[str] = "100 g"
    verification_interval: Optional[str] = "12 Months"
    accuracy_class: str
    statutory_fee: float
    status: str
    scheduled_date: Optional[str] = None
    contact_person: Optional[str] = None
    contact_phone: Optional[str] = None
    owner_name: Optional[str] = None
    owner_phone: Optional[str] = None
    latest_certificate_number: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

# INSPECTION SCHEMAS
class InspectionCreate(BaseModel):
    instrument_id: int
    inspector_id: int
    inspector_latitude: float
    inspector_longitude: float
    zero_setting_test: bool = True
    repeatability_test: bool = True
    eccentricity_corner_test: bool = True
    iot_reading_captured: Optional[float] = None
    max_error_observed: float = 0.0
    permissible_error_limit: float = 1.0
    photo_proof_path: Optional[str] = None
    inspector_remarks: Optional[str] = "Instrument thoroughly inspected and verified compliant as per Legal Metrology rules."

class InspectionResponse(BaseModel):
    id: int
    instrument_id: int
    inspector_id: int
    inspection_date: datetime
    distance_from_shop_meters: float
    is_geofence_passed: bool
    zero_setting_test: bool
    repeatability_test: bool
    eccentricity_corner_test: bool
    iot_reading_captured: Optional[float]
    status: str
    photo_proof_path: Optional[str]
    inspector_remarks: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class InspectionHistoryResponse(BaseModel):
    id: int
    instrument_id: int
    inspection_date: datetime
    status: str
    shop_name: str
    shop_address: str
    district: str
    serial_number: str
    instrument_type: str
    brand_make: str
    max_capacity: str
    inspector_name: str
    inspector_badge: str
    certificate_number: Optional[str] = None
    distance_from_shop_meters: float
    iot_reading_captured: Optional[float] = None
    max_error_observed: float = 0.0
    permissible_error_limit: float = 1.0
    photo_proof_path: Optional[str] = None
    inspector_remarks: Optional[str] = None
    created_at: datetime

# CERTIFICATE SCHEMAS
class CertificateResponse(BaseModel):
    id: int
    certificate_number: str
    instrument_id: int
    inspection_id: int
    issue_date: datetime
    expiry_date: datetime
    qr_code_filename: str
    data_hash: str
    cryptographic_signature: str
    is_active: bool

    class Config:
        from_attributes = True

# COMPLAINT SCHEMAS
class ComplaintCreate(BaseModel):
    instrument_id: Optional[int] = None
    complainant_name: str
    complainant_phone: str
    complainant_email: Optional[str] = None
    complaint_type: str
    description: str
    photo_evidence: Optional[str] = None

class ComplaintResponse(BaseModel):
    id: int
    complaint_id: str
    instrument_id: Optional[int]
    complainant_name: str
    complaint_type: str
    description: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

# IOT TELEMETRY SCHEMA
class ScaleReadingPayload(BaseModel):
    weight: float
    unit: str = "kg"
    is_stable: bool = True
    tare: float = 0.0
    device_id: str
