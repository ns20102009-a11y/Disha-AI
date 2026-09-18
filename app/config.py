import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / 'data'
DATA_DIR.mkdir(exist_ok=True)

STATIC_DIR = BASE_DIR / 'app' / 'static'
QR_DIR = STATIC_DIR / 'qr_codes'
UPLOADS_DIR = STATIC_DIR / 'uploads'
QR_DIR.mkdir(parents=True, exist_ok=True)
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

DATABASE_URL = os.getenv('DATABASE_URL', f'sqlite:///{DATA_DIR}/metrology.db')
SECRET_KEY = os.getenv('SECRET_KEY', 'emapan-national-legal-metrology-secret-key-ed25519-auth')

# Legal Metrology Fee Slabs (Schedule of Fees, Rules 2011)
STATUTORY_FEES = {
    'COUNTER_SCALE_LE_50KG': {'name': 'Non-Automatic Counter Scale (<= 50kg)', 'fee': 200, 'validity_months': 12},
    'PLATFORM_SCALE_50_500KG': {'name': 'Platform Scale (50kg - 500kg)', 'fee': 500, 'validity_months': 12},
    'PLATFORM_SCALE_500_5000KG': {'name': 'Industrial Heavy Platform (500kg - 5000kg)', 'fee': 1000, 'validity_months': 12},
    'WEIGHBRIDGE_LE_50TON': {'name': 'Electronic Weighbridge (<= 50 Tonnes)', 'fee': 3000, 'validity_months': 12},
    'WEIGHBRIDGE_GT_50TON': {'name': 'Electronic Weighbridge (> 50 Tonnes)', 'fee': 5000, 'validity_months': 12},
    'FUEL_DISPENSER_NOZZLE': {'name': 'Automated Fuel Dispenser (Per Nozzle)', 'fee': 1500, 'validity_months': 12},
    'GOLD_PRECISION_SCALE': {'name': 'High Precision Jewellery Balance (Class II)', 'fee': 400, 'validity_months': 12},
}

GEOFENCE_MAX_DISTANCE_METERS = 150  # Must be within 150m of shop for valid inspection
SYSTEM_NAME = 'DISHA AI'
SYSTEM_SUBTITLE = 'National Online Verification & Stamping Portal for Legal Metrology'
