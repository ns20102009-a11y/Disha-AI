import hmac
import hashlib
import json
import base64
from pathlib import Path
import qrcode
from PIL import Image, ImageDraw, ImageFont
from app.config import SECRET_KEY, QR_DIR

def generate_data_hash(payload: dict) -> str:
    """
    Computes a canonical SHA-256 hash of certificate payload dictionary.
    """
    canonical_json = json.dumps(payload, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(canonical_json.encode('utf-8')).hexdigest()

def sign_certificate_payload(payload: dict) -> tuple[str, str]:
    """
    Returns (data_hash, cryptographic_signature) using HMAC-SHA256.
    """
    data_hash = generate_data_hash(payload)
    signature = hmac.new(
        SECRET_KEY.encode('utf-8'),
        data_hash.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    return data_hash, signature

def verify_certificate_signature(payload: dict, expected_signature: str) -> bool:
    """
    Verifies that the certificate data has not been modified/forged.
    """
    data_hash = generate_data_hash(payload)
    computed_sig = hmac.new(
        SECRET_KEY.encode('utf-8'),
        data_hash.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(computed_sig, expected_signature)

def generate_qr_code(certificate_number: str, verify_url: str) -> str:
    """
    Generates a secure QR Code image with legal metrology branding.
    Returns relative web path to static QR image.
    """
    filename = f"qr_{certificate_number.replace('-', '_')}.png"
    filepath = QR_DIR / filename

    # Configure high error correction to allow clean scanning even if printed & worn
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=3,
    )
    qr.add_data(verify_url)
    qr.make(fit=True)

    # Use Government Blue/Navy color for official appearance
    img = qr.make_image(fill_color="#0F2942", back_color="white").convert('RGB')
    
    # Save QR code
    img.save(filepath)
    return f"/static/qr_codes/{filename}"
