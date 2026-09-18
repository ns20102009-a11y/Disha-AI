import sys
from pathlib import Path
from fastapi.testclient import TestClient

from app.main import app
from app.database import SessionLocal
from app import models

client = TestClient(app)

def run_tests():
    print("--- 1. Testing Web Pages ---")
    pages = ["/", "/trader", "/inspector", "/admin"]
    for p in pages:
        res = client.get(p)
        assert res.status_code == 200, f"Failed {p}: {res.status_code}"
        print(f"  [OK] GET {p} (200)")

    print("\n--- 2. Testing API Endpoints ---")
    res = client.get("/api/instruments/")
    assert res.status_code == 200
    inst_count = len(res.json())
    print(f"  [OK] GET /api/instruments/ ({inst_count} registered)")

    res = client.get("/api/inspections/pending")
    assert res.status_code == 200
    pending_count = len(res.json())
    print(f"  [OK] GET /api/inspections/pending ({pending_count} pending)")

    res = client.get("/api/analytics")
    assert res.status_code == 200
    stats = res.json()
    print(f"  [OK] GET /api/analytics (Compliance: {stats.get('compliance_rate')}%)")

    print("\n--- 3. Testing Certificate & Cryptographic Verification ---")
    db = SessionLocal()
    cert = db.query(models.Certificate).first()
    db.close()

    if cert:
        cnum = cert.certificate_number
        res = client.get(f"/api/certificates/{cnum}")
        assert res.status_code == 200
        print(f"  [OK] GET /api/certificates/{cnum}")

        res = client.get(f"/api/certificates/{cnum}/verify-tamper")
        assert res.status_code == 200
        assert res.json()["is_cryptographically_valid"] is True
        print(f"  [OK] Cryptographic Signature Verified: TRUE")

        res = client.get(f"/verify/{cnum}")
        assert res.status_code == 200
        print(f"  [OK] GET /verify/{cnum} (Citizen Trust Badge)")

        res = client.get(f"/certificate/{cnum}")
        assert res.status_code == 200
        print(f"  [OK] GET /certificate/{cnum} (Form-VIII Certificate)")

        res = client.get(f"/sticker/{cnum}")
        assert res.status_code == 200
        print(f"  [OK] GET /sticker/{cnum} (Printable Scale Sticker)")

    print("\n--- 4. Testing Phase 2 Automated Notification Engine ---")
    res = client.post("/api/notifications/trigger-expiry-check")
    assert res.status_code == 200
    print("  [OK] POST /api/notifications/trigger-expiry-check (Expiry Scanner Triggered)")

    res = client.get("/api/notifications/logs")
    assert res.status_code == 200
    print(f"  [OK] GET /api/notifications/logs ({len(res.json())} alert logs retrieved)")

    print("\n--- 5. Testing Phase 3 Grand Finale Endpoints ---")
    res = client.get("/pitch")
    assert res.status_code == 200
    print("  [OK] GET /pitch (In-Browser Pitch Deck)")

    res = client.get("/api/vigilance/audit")
    assert res.status_code == 200
    vig_data = res.json()
    print(f"  [OK] GET /api/vigilance/audit (Anomalies detected: {vig_data.get('total_anomalies_detected')})")

    res = client.post("/api/vigilance/order-raid/INST-2026-TEST")
    assert res.status_code == 200
    print("  [OK] POST /api/vigilance/order-raid/INST-2026-TEST (Surprise Raid Authorized)")

    res = client.post("/api/demo/scenario/expired")
    assert res.status_code == 200
    print("  [OK] POST /api/demo/scenario/expired (Scenario 2: Expired Stamping)")

    res = client.post("/api/demo/scenario/compliant")
    assert res.status_code == 200
    print("  [OK] POST /api/demo/scenario/compliant (Scenario 1: Reset to Compliant)")

    print("\n--- 6. Testing Master Multi-Stakeholder Modules ---")
    pages_master = ["/manufacturer", "/grievances", "/scale-simulator"]
    for pm in pages_master:
        res = client.get(pm)
        assert res.status_code == 200, f"Failed {pm}"
        print(f"  [OK] GET {pm} (200)")

    res = client.get("/api/manufacturers/models")
    assert res.status_code == 200
    print(f"  [OK] GET /api/manufacturers/models ({len(res.json())} approved models found)")

    res = client.post("/api/manufacturers/models", json={
        "manufacturer_name": "Phoenix Scales India",
        "brand_name": "Phoenix Gold-600",
        "instrument_type": "Jewellery Balance",
        "accuracy_class": "Class II",
        "max_capacity": "600 g",
        "rrsl_testing_lab": "RRSL Faridabad (Govt of India)"
    })
    assert res.status_code == 200
    print("  [OK] POST /api/manufacturers/models (New Model Application Approved)")

    res = client.get("/api/manufacturers/verify-model/IND/09/2021/418")
    assert res.status_code == 200
    assert res.json()["is_valid"] is True
    print("  [OK] GET /api/manufacturers/verify-model/IND/09/2021/418 (Model Verified Genuine)")

    if cert:
        res = client.get(f"/api/certificates/{cnum}/download-pdf")
        assert res.status_code == 200
        assert res.headers["content-type"] == "application/pdf"
        print(f"  [OK] GET /api/certificates/{cnum}/download-pdf (Genuine Binary PDF Generated: {len(res.content)} bytes)")

    print("\n--- 7. Testing ProductGuard AI (Multi-Sector: Health, Baby Products, Food) ---")
    res = client.get("/productguard")
    assert res.status_code == 200
    print("  [OK] GET /productguard (Web Application UI)")

    res = client.get("/api/productguard/test-cases")
    assert res.status_code == 200
    test_cases = res.json()
    assert len(test_cases) >= 10
    print(f"  [OK] GET /api/productguard/test-cases ({len(test_cases)} multi-sector presets available)")

    # 1. Food & Dairy: Amul Taaza Safe
    res = client.post("/api/productguard/simulate-ocr", json={"preset_id": "test1"})
    assert res.status_code == 200
    tc1 = res.json()
    assert tc1["intelligence"]["verdict"] == "SAFE"
    print(f"  [OK] Food Verified: {tc1['product']['product_name']} -> [SAFE] {tc1['intelligence']['verdict']}")

    # 2. Food: Harvest Bread Expiring Soon
    res = client.post("/api/productguard/simulate-ocr", json={"preset_id": "test2"})
    assert res.status_code == 200
    tc2 = res.json()
    assert tc2["intelligence"]["verdict"] == "EXPIRING_SOON"
    print(f"  [OK] Food Verified: {tc2['product']['product_name']} -> [EXPIRING] {tc2['intelligence']['verdict']}")

    # 3. Health Sector: Coldrif Syrup Toxic DEG Recall
    res = client.post("/api/productguard/simulate-ocr", json={"preset_id": "test3"})
    assert res.status_code == 200
    tc3 = res.json()
    assert tc3["intelligence"]["verdict"] == "CRITICAL_RECALL"
    assert tc3["batch"]["is_recalled"] is True
    print(f"  [OK] Health Verified: {tc3['product']['product_name']} (SR-13) -> [RECALL] {tc3['intelligence']['verdict']}")

    # 4. Health Sector: Spurious Azicip (Counterfeit 0% API)
    res = client.post("/api/productguard/simulate-ocr", json={"preset_id": "test_azithro_fake"})
    assert res.status_code == 200
    tc_fake = res.json()
    assert tc_fake["intelligence"]["verdict"] == "CRITICAL_RECALL"
    print(f"  [OK] Health Verified: Spurious Azicip (AZ-8029) -> [RECALL] {tc_fake['intelligence']['verdict']}")

    # 5. Health Sector: Genuine Azicip (Safe 99.8% HPLC)
    res = client.post("/api/productguard/simulate-ocr", json={"preset_id": "test_azithro_safe"})
    assert res.status_code == 200
    tc_safe_med = res.json()
    assert tc_safe_med["intelligence"]["verdict"] == "SAFE"
    print(f"  [OK] Health Verified: Genuine Azicip (AZ-8021) -> [SAFE] {tc_safe_med['intelligence']['verdict']}")

    # 6. Health Sector: Lantus Insulin Cold-Chain Thermal Failure
    res = client.post("/api/productguard/simulate-ocr", json={"preset_id": "test_insulin"})
    assert res.status_code == 200
    tc_ins = res.json()
    assert tc_ins["intelligence"]["verdict"] == "CRITICAL_RECALL"
    print(f"  [OK] Health Verified: Lantus Insulin (LT-1108) -> [RECALL] {tc_ins['intelligence']['verdict']}")

    # 7. Baby Products: Nestlé Lactogen Formula (Safe / Zero Cronobacter)
    res = client.post("/api/productguard/simulate-ocr", json={"preset_id": "test_lactogen"})
    assert res.status_code == 200
    tc_lac = res.json()
    assert tc_lac["intelligence"]["verdict"] == "SAFE"
    print(f"  [OK] Baby Product Verified: {tc_lac['product']['product_name']} -> [SAFE] {tc_lac['intelligence']['verdict']}")

    # 8. Baby Products: Nestlé Cerelac (Excess Added Sugar Regulatory Recall)
    res = client.post("/api/productguard/simulate-ocr", json={"preset_id": "test_cerelac"})
    assert res.status_code == 200
    tc_cer = res.json()
    assert tc_cer["intelligence"]["verdict"] == "CRITICAL_RECALL"
    print(f"  [OK] Baby Product Verified: Cerelac Wheat-Apple (CER-892) -> [RECALL] {tc_cer['intelligence']['verdict']}")

    # 9. Baby Products: Woodward's Gripe Water Contaminated
    res = client.post("/api/productguard/simulate-ocr", json={"preset_id": "test_gripe_bad"})
    assert res.status_code == 200
    tc_grp = res.json()
    assert tc_grp["intelligence"]["verdict"] == "CRITICAL_RECALL"
    print(f"  [OK] Baby Product Verified: Woodward's Gripe (WD-2049) -> [RECALL] {tc_grp['intelligence']['verdict']}")

    # 10. CDSCO & Infant Safety Alerts Endpoints
    res = client.get("/api/productguard/cdsco-alerts")
    assert res.status_code == 200
    cdsco_alerts = res.json()
    assert len(cdsco_alerts) >= 3
    print(f"  [OK] GET /api/productguard/cdsco-alerts ({len(cdsco_alerts)} CDSCO NSQ drug alerts active)")

    res = client.get("/api/productguard/infant-safety-alerts")
    assert res.status_code == 200
    infant_alerts = res.json()
    assert len(infant_alerts) >= 3
    print(f"  [OK] GET /api/productguard/infant-safety-alerts ({len(infant_alerts)} infant safety directives active)")

    # 11. Sector Data Endpoints
    res = client.get("/api/productguard/sector-data?sector=HEALTH_PHARMA")
    assert res.status_code == 200
    h_data = res.json()
    assert h_data["total_products"] >= 5
    print(f"  [OK] GET /api/productguard/sector-data (Health: {h_data['total_products']} products, {h_data['recalled_batches']} recalls)")

    res = client.get("/api/productguard/sector-data?sector=BABY_PRODUCTS")
    assert res.status_code == 200
    b_data = res.json()
    assert b_data["total_products"] >= 5
    print(f"  [OK] GET /api/productguard/sector-data (Baby Products: {b_data['total_products']} products, {b_data['recalled_batches']} recalls)")

    # 12. Consumer Grievance Filing with Sector & Adverse Event
    res = client.post("/api/productguard/grievance", json={
        "sector": "HEALTH_PHARMA",
        "batch_number": "AZ-8029",
        "product_name": "Azicip-500 Spurious Batch",
        "shop_name": "Shree Ram Medicos",
        "shop_location": "Sector 15, Faridabad",
        "issue_category": "Spurious / Fake Medicine",
        "adverse_health_event": True,
        "patient_age_group": "Adult",
        "description": "Patient fever aggravated after taking fake chalk tablet.",
        "consumer_phone": "+91 98765 43210"
    })
    assert res.status_code == 200
    griev_docket = res.json()["docket_number"]
    print(f"  [OK] POST /api/productguard/grievance (Docket Issued: {griev_docket})")

    # 13. Live Docket Pipeline Tracker
    res = client.get(f"/api/productguard/grievances/track/{griev_docket}")
    assert res.status_code == 200
    track_data = res.json()
    assert len(track_data["pipeline"]) == 4
    print(f"  [OK] GET /api/productguard/grievances/track/{griev_docket} (4-Stage Pipeline Verified)")

    res = client.get("/api/productguard/grievances/track/PG-GRIEV-2026-1082")
    assert res.status_code == 200
    g1082 = res.json()
    assert g1082["docket"]["status"] == "RESOLVED"
    print("  [OK] GET /api/productguard/grievances/track/PG-GRIEV-2026-1082 (Stage 4 Seizure Verified)")

    # 14. Retailer Mode Inventory
    res = client.get("/api/productguard/inventory")
    assert res.status_code == 200
    inv_items = res.json()
    assert len(inv_items) >= 10
    print(f"  [OK] GET /api/productguard/inventory ({len(inv_items)} shelf inventory records tracked)")

    first_inv_id = inv_items[0]["id"]
    res = client.post(f"/api/productguard/inventory/{first_inv_id}/toggle-removal")
    assert res.status_code == 200
    print(f"  [OK] POST /api/productguard/inventory/{first_inv_id}/toggle-removal (Marked for distributor return)")

    # 15. Stats
    res = client.get("/api/productguard/stats")
    assert res.status_code == 200
    stats = res.json()
    assert stats["total_products"] >= 15
    print(f"  [OK] GET /api/productguard/stats (Products: {stats['total_products']}, Recalls: {stats['recalled_batches']})")

    print("\n=======================================================")
    print("  ALL VERIFICATION TESTS COMPLETED SUCCESSFULLY (100%)")
    print("=======================================================")

if __name__ == "__main__":
    run_tests()
