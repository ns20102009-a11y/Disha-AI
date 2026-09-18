from datetime import datetime, timedelta
from typing import List, Dict
from sqlalchemy.orm import Session
from app import models
from app.services.geofence_service import calculate_haversine_distance

def run_ai_vigilance_audit(db: Session) -> Dict:
    """
    AI Anomaly & Vigilance Surveillance Engine:
    1. Detects 'Impossible Speed / Ghost Inspections' (Inspector approving distant shops in unrealistically short time).
    2. Detects 'Complaint Clusters' (Multiple consumers reporting short-weighing at the same establishment).
    3. Computes Risk Indices for automated enforcement audits.
    """
    anomalies = []
    
    # 1. Check Inspection Velocity Anomalies
    inspections = db.query(models.InspectionRecord).order_by(models.InspectionRecord.id.asc()).all()
    for i in range(1, len(inspections)):
        prev_insp = inspections[i - 1]
        curr_insp = inspections[i]
        
        # If inspected by same inspector
        if prev_insp.inspector_id == curr_insp.inspector_id:
            time_diff_hours = (curr_insp.inspection_date - prev_insp.inspection_date).total_seconds() / 3600.0
            dist_km = calculate_haversine_distance(
                prev_insp.inspector_latitude, prev_insp.inspector_longitude,
                curr_insp.inspector_latitude, curr_insp.inspector_longitude
            ) / 1000.0

            # If velocity exceeds 90 km/h in city traffic, flag as suspicious
            if time_diff_hours > 0 and (dist_km / time_diff_hours) > 90.0:
                anomalies.append({
                    "type": "IMPOSSIBLE_TRAVEL_VELOCITY",
                    "severity": "HIGH",
                    "inspector_badge": curr_insp.inspector.badge_number,
                    "inspector_name": curr_insp.inspector.full_name,
                    "description": f"Inspector covered {dist_km:.1f} km in {time_diff_hours*60:.0f} mins (Calculated speed: {dist_km/time_diff_hours:.0f} km/h). Suspected table inspection.",
                    "action_recommended": "Hold certificate issuance & order GPS telemetry re-audit."
                })

    # 2. Check Consumer Grievance Spikes
    instruments = db.query(models.Instrument).all()
    for inst in instruments:
        open_complaints = db.query(models.Complaint).filter(
            models.Complaint.instrument_id == inst.id,
            models.Complaint.status == "OPEN"
        ).count()

        if open_complaints >= 1:
            risk_score = min(40 + (open_complaints * 25), 98)
            anomalies.append({
                "type": "SHORT_WEIGHING_COMPLAINT_CLUSTER",
                "severity": "CRITICAL" if risk_score > 70 else "MEDIUM",
                "instrument_uid": inst.instrument_uid,
                "shop_name": inst.shop_name,
                "district": inst.district,
                "serial_number": inst.serial_number,
                "risk_score": risk_score,
                "description": f"{open_complaints} active consumer grievance(s) logged regarding suspected weight manipulation.",
                "action_recommended": "Dispatch Enforcement Flying Squad for surprise calibration audit."
            })

    # Overall system health score
    overall_health = max(100 - (len(anomalies) * 12), 40)

    return {
        "status": "completed",
        "audit_timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        "total_anomalies_detected": len(anomalies),
        "national_integrity_score": f"{overall_health}%",
        "anomalies": anomalies
    }
