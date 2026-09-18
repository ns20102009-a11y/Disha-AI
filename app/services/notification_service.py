from datetime import datetime, timedelta
from typing import List, Dict
from sqlalchemy.orm import Session
from app import models

# In-memory alert dispatch audit log
NOTIFICATION_LOGS: List[Dict] = []

def check_and_dispatch_expiry_alerts(db: Session) -> Dict:
    """
    Scans all registered instruments and dispatches simulated WhatsApp & SMS
    alerts for certificates expiring soon (within 30 days) or overdue.
    """
    certificates = db.query(models.Certificate).filter(models.Certificate.is_active == True).all()
    now = datetime.utcnow()
    dispatched_count = 0

    for cert in certificates:
        days_left = (cert.expiry_date - now).days
        inst = cert.instrument
        owner = inst.owner

        # Check if expiring within 30 days or overdue
        if days_left <= 30:
            urgency = "CRITICAL (OVERDUE)" if days_left < 0 else (
                "URGENT (15 Days Left)" if days_left <= 15 else "REMINDER (30 Days Left)"
            )

            # 1. WhatsApp Template Message
            wa_message = (
                f"🏛️ *GOVERNMENT OF INDIA - LEGAL METROLOGY DIVISION*\n"
                f"Dear {owner.full_name},\n"
                f"Stamping validity for your instrument *{inst.brand_make}* (Serial: *{inst.serial_number}*) "
                f"at *{inst.shop_name}* expires in *{max(days_left, 0)} days* ({cert.expiry_date.strftime('%d-%b-%Y')}).\n\n"
                f"⚠️ *Legal Warning:* Commercial use without re-verification violates Section 24 of Legal Metrology Act, 2009 (Fine up to ₹25,000).\n"
                f"📲 *Renew Online Now:* http://127.0.0.1:8000/trader"
            )

            # 2. SMS Alert Template
            sms_message = (
                f"Govt of India (Legal Metrology): Re-verification for scale {inst.serial_number} "
                f"due on {cert.expiry_date.strftime('%d/%m/%Y')}. Renew online to avoid penalty: http://127.0.0.1:8000/trader"
            )

            record = {
                "id": len(NOTIFICATION_LOGS) + 1,
                "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                "instrument_uid": inst.instrument_uid,
                "serial_number": inst.serial_number,
                "shop_name": inst.shop_name,
                "owner_name": owner.full_name,
                "phone": owner.phone,
                "days_remaining": days_left,
                "urgency": urgency,
                "channels": ["WhatsApp (Green Tick)", "National SMS Gateway"],
                "whatsapp_body": wa_message,
                "sms_body": sms_message,
                "status": "DELIVERED"
            }

            NOTIFICATION_LOGS.insert(0, record)
            dispatched_count += 1

    # Keep last 50 logs
    del NOTIFICATION_LOGS[50:]

    return {
        "status": "success",
        "scanned_certificates": len(certificates),
        "dispatched_alerts": dispatched_count,
        "timestamp": datetime.utcnow().isoformat()
    }

def get_notification_logs() -> List[Dict]:
    return NOTIFICATION_LOGS
