from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    phone = Column(String(20), nullable=False)
    role = Column(String(20), nullable=False)  # TRADER, INSPECTOR, ADMIN
    badge_number = Column(String(50), nullable=True) # For LMO inspector
    jurisdiction_district = Column(String(100), nullable=True)
    jurisdiction_state = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    instruments = relationship('Instrument', back_populates='owner')
    inspections = relationship('InspectionRecord', back_populates='inspector')

class Instrument(Base):
    __tablename__ = 'instruments'

    id = Column(Integer, primary_key=True, index=True)
    instrument_uid = Column(String(50), unique=True, index=True, nullable=False)
    owner_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    shop_name = Column(String(150), nullable=False)
    trade_license_no = Column(String(100), nullable=False)
    shop_address = Column(Text, nullable=False)
    district = Column(String(100), nullable=False)
    state = Column(String(100), nullable=False)
    pincode = Column(String(10), nullable=False)
    
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    
    instrument_type = Column(String(50), nullable=False)
    brand_make = Column(String(100), nullable=False)
    model_approval_number = Column(String(100), nullable=False)
    serial_number = Column(String(100), unique=True, index=True, nullable=False)
    max_capacity = Column(String(50), nullable=False)
    min_capacity = Column(String(50), nullable=True)
    verification_interval = Column(String(50), nullable=True)
    accuracy_class = Column(String(20), default='Class III')
    
    statutory_fee = Column(Float, default=200.0)
    status = Column(String(40), default='PENDING_VERIFICATION') # PENDING_VERIFICATION, INSPECTION_SCHEDULED, VERIFIED, EXPIRED, REJECTED
    scheduled_date = Column(String(100), nullable=True) # e.g. "Today, 10:30 AM - 11:30 AM"
    contact_person = Column(String(100), nullable=True)
    contact_phone = Column(String(20), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship('User', back_populates='instruments')
    inspections = relationship('InspectionRecord', back_populates='instrument')
    certificates = relationship('Certificate', back_populates='instrument')
    complaints = relationship('Complaint', back_populates='instrument')

    @property
    def owner_name(self):
        if self.contact_person:
            return self.contact_person
        return self.owner.full_name if self.owner else "Authorized Trader"

    @property
    def owner_phone(self):
        if self.contact_phone:
            return self.contact_phone
        return self.owner.phone if self.owner else "+91 98765 43210"

    @property
    def latest_certificate_number(self):
        if self.certificates and len(self.certificates) > 0:
            return self.certificates[-1].certificate_number
        return None

class InspectionRecord(Base):
    __tablename__ = 'inspection_records'

    id = Column(Integer, primary_key=True, index=True)
    instrument_id = Column(Integer, ForeignKey('instruments.id'), nullable=False)
    inspector_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    inspection_date = Column(DateTime, default=datetime.utcnow)
    inspector_latitude = Column(Float, nullable=False)
    inspector_longitude = Column(Float, nullable=False)
    distance_from_shop_meters = Column(Float, nullable=False)
    is_geofence_passed = Column(Boolean, default=True)

    # OIML R-76 Technical Tests
    zero_setting_test = Column(Boolean, default=True)
    repeatability_test = Column(Boolean, default=True)
    eccentricity_corner_test = Column(Boolean, default=True)
    iot_reading_captured = Column(Float, nullable=True)
    max_error_observed = Column(Float, default=0.0)
    permissible_error_limit = Column(Float, default=1.0)
    
    photo_proof_path = Column(String(255), nullable=True)
    inspector_remarks = Column(Text, nullable=True)
    status = Column(String(30), default='PASSED') # PASSED, FAILED
    created_at = Column(DateTime, default=datetime.utcnow)

    instrument = relationship('Instrument', back_populates='inspections')
    inspector = relationship('User', back_populates='inspections')
    certificate = relationship('Certificate', back_populates='inspection', uselist=False)

class Certificate(Base):
    __tablename__ = 'certificates'

    id = Column(Integer, primary_key=True, index=True)
    certificate_number = Column(String(100), unique=True, index=True, nullable=False)
    instrument_id = Column(Integer, ForeignKey('instruments.id'), nullable=False)
    inspection_id = Column(Integer, ForeignKey('inspection_records.id'), nullable=False)
    
    issue_date = Column(DateTime, default=datetime.utcnow)
    expiry_date = Column(DateTime, nullable=False)
    qr_code_filename = Column(String(255), nullable=False)
    data_hash = Column(String(64), nullable=False)
    cryptographic_signature = Column(String(256), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    instrument = relationship('Instrument', back_populates='certificates')
    inspection = relationship('InspectionRecord', back_populates='certificate')

class Complaint(Base):
    __tablename__ = 'complaints'

    id = Column(Integer, primary_key=True, index=True)
    complaint_id = Column(String(50), unique=True, index=True, nullable=False)
    instrument_id = Column(Integer, ForeignKey('instruments.id'), nullable=True)
    
    complainant_name = Column(String(100), nullable=False)
    complainant_phone = Column(String(20), nullable=False)
    complainant_email = Column(String(100), nullable=True)
    complaint_type = Column(String(50), nullable=False)
    description = Column(Text, nullable=False)
    photo_evidence = Column(String(255), nullable=True)
    status = Column(String(30), default='OPEN') # OPEN, INVESTIGATING, RESOLVED, DISMISSED
    admin_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    instrument = relationship('Instrument', back_populates='complaints')

class ModelApproval(Base):
    __tablename__ = 'model_approvals'

    id = Column(Integer, primary_key=True, index=True)
    approval_number = Column(String(100), unique=True, index=True, nullable=False) # e.g. IND/09/2022/418
    manufacturer_name = Column(String(150), nullable=False)
    brand_name = Column(String(100), nullable=False)
    instrument_type = Column(String(100), nullable=False)
    accuracy_class = Column(String(50), default='Class III')
    max_capacity = Column(String(50), nullable=False)
    rrsl_testing_lab = Column(String(150), default='RRSL Faridabad (Govt of India)')
    oiml_recommendation = Column(String(50), default='OIML R-76-1:2006')
    validity_years = Column(Integer, default=10)
    status = Column(String(30), default='APPROVED') # APPROVED, UNDER_TESTING, REVOKED
    issue_date = Column(DateTime, default=datetime.utcnow)

# -------------------------------------------------------------
# PRODUCTGUARD AI: PRODUCT SAFETY & BATCH VERIFICATION MODELS
# -------------------------------------------------------------

class PGProduct(Base):
    __tablename__ = 'pg_products'

    id = Column(Integer, primary_key=True, index=True)
    barcode = Column(String(50), unique=True, index=True, nullable=False)
    brand_name = Column(String(100), nullable=False)
    product_name = Column(String(150), nullable=False)
    sector = Column(String(50), default="FOOD_CONSUMABLES", index=True) # HEALTH_PHARMA, BABY_PRODUCTS, FOOD_CONSUMABLES
    category = Column(String(50), nullable=False) # Dairy, Medicine, Baby Food, Bakery, Edible Oil, etc.
    sub_category = Column(String(100), nullable=True) # e.g. Infant Milk Formula, Antibiotic, Paediatric Syrup
    fssai_license = Column(String(100), nullable=False) # FSSAI or CDSCO Drug Mfg Lic
    net_quantity = Column(String(50), nullable=False)
    mrp = Column(Float, nullable=False)
    image_url = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    batches = relationship('PGBatch', back_populates='product')

class PGBatch(Base):
    __tablename__ = 'pg_batches'

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey('pg_products.id'), nullable=False)
    batch_number = Column(String(50), index=True, nullable=False)
    mfg_date = Column(DateTime, nullable=False)
    expiry_date = Column(DateTime, nullable=False)
    status = Column(String(30), default='SAFE') # SAFE, EXPIRING_SOON, RECALLED, EXPIRED
    is_recalled = Column(Boolean, default=False)
    recall_reason = Column(Text, nullable=True)
    regulatory_authority = Column(String(150), default="FSSAI Central Authority & State FDA")
    lab_test_report_id = Column(String(100), nullable=True)
    lab_test_summary = Column(Text, nullable=True)
    hazard_level = Column(String(30), default='NONE') # NONE, MODERATE, CRITICAL
    storage_temperature = Column(String(100), default="Ambient (<25°C)")
    adverse_events_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    product = relationship('PGProduct', back_populates='batches')
    inventory_items = relationship('PGInventory', back_populates='batch')

class PGGrievance(Base):
    __tablename__ = 'pg_grievances'

    id = Column(Integer, primary_key=True, index=True)
    docket_number = Column(String(50), unique=True, index=True, nullable=False)
    batch_number = Column(String(50), nullable=False)
    product_name = Column(String(150), nullable=False)
    sector = Column(String(50), default="FOOD_CONSUMABLES", index=True) # HEALTH_PHARMA, BABY_PRODUCTS, FOOD_CONSUMABLES
    shop_name = Column(String(150), nullable=False)
    shop_location = Column(String(255), nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    issue_category = Column(String(100), nullable=False) # Expired on Shelf, Spurious / Fake Medicine, Toxic Contamination, High Sugar / Microbial
    description = Column(Text, nullable=False)
    adverse_health_event = Column(Boolean, default=False)
    patient_age_group = Column(String(50), nullable=True) # Infant (0-1 yr), Child, Adult
    photo_url = Column(String(255), nullable=True)
    consumer_phone = Column(String(20), nullable=True)
    status = Column(String(30), default='REGISTERED') # REGISTERED, INVESTIGATING, SEIZURE_DISPATCHED, RESOLVED
    pipeline_stage = Column(Integer, default=1) # 1 to 4
    investigating_officer = Column(String(150), nullable=True)
    resolution_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class PGInventory(Base):
    __tablename__ = 'pg_inventory'

    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(Integer, ForeignKey('pg_batches.id'), nullable=False)
    store_name = Column(String(150), nullable=False)
    store_location = Column(String(255), nullable=False)
    stock_quantity = Column(Integer, default=1)
    marked_for_removal = Column(Boolean, default=False)
    last_scanned_at = Column(DateTime, default=datetime.utcnow)

    batch = relationship('PGBatch', back_populates='inventory_items')


