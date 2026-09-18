from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.notification_service import check_and_dispatch_expiry_alerts, get_notification_logs

router = APIRouter(prefix="/api/notifications", tags=["Notifications & Alerts"])

@router.post("/trigger-expiry-check")
def trigger_expiry_check(db: Session = Depends(get_db)):
    """
    Triggers automated scan of all registered weighing scales and dispatches
    statutory SMS/WhatsApp re-verification reminder notices.
    """
    return check_and_dispatch_expiry_alerts(db)

@router.get("/logs")
def fetch_notification_logs():
    """
    Returns the real-time delivery audit log of SMS & WhatsApp alerts dispatched.
    """
    return get_notification_logs()
