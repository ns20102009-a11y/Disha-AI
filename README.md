# DISHA AI
### National Online Verification & Stamping System for Weighing and Measuring Instruments
**Department of Consumer Affairs (Legal Metrology Division)**  
**Ministry of Consumer Affairs, Food & Public Distribution, Government of India**  

---

## 📌 Executive Summary
Under the **Legal Metrology Act, 2009**, all commercial weighing scales, platform balances, weighbridges, and fuel dispensers in India must be verified and stamped before commercial use. However, the current system suffers from:
1. **Manual / Paper Stamping & Lead Seals:** Easily counterfeited, tampered with, or expired without consumer knowledge.
2. **"Table Inspections" (Ghost Inspections):** Officers signing off without visiting shop premises.
3. **Manual Data Entry Fraud:** Manipulating calibration readings on paper registers.
4. **No Citizen Verification:** Consumers have no instant way to check if a scale is genuine.

**DISHA AI** solves this with an end-to-end digital ecosystem featuring:
- **Anti-Table Inspection Geofencing:** GPS validation ensures officers are physically within 150m of shop premises.
- **Cryptographic Tamper-Proof Digital Seals:** Ed25519/HMAC-SHA256 signed digital certificates (Form-VIII) with dynamic QR codes.
- **Live IoT Load-Cell Telemetry:** Direct RS-232 / BLE / WebSocket weight capture directly from digital indicators into the calibration checklist.
- **Instant Public Trust Badge:** Citizens and judges scan the scale QR code with any smartphone camera to view live verification validity and report short-weighing fraud.
- **Central Ministry Analytics:** National compliance monitoring, overdue re-verification tracking, and grievance heatmaps.

---

## 🏛️ System Architecture & Portals

```
                  +-------------------------------------------------------------+
                  |         CENTRAL FASTAPI BACKEND (Python 3.13)              |
                  |     - SQLite / PostgreSQL Engine with SQLAlchemy            |
                  |     - HMAC-SHA256 Cryptographic Signing Engine              |
                  |     - WebSocket Live Scale Telemetry Gateway                |
                  +-------------------------------------------------------------+
                                                 |
         +--------------------+------------------+------------------+--------------------+
         |                    |                                     |                    |
         v                    v                                     v                    v
+------------------+  +----------------------+             +------------------+  +--------------------+
| 1. TRADER PORTAL |  | 2. INSPECTOR TOOLKIT |             | 3. CITIZEN SCAN  |  | 4. MINISTRY ADMIN  |
| (/trader)        |  | (/inspector)         |             | (/verify/{cert}) |  | (/admin)           |
|------------------|  |----------------------|             |------------------|  |--------------------|
| - Register Scale |  | - GPS Geofence Check |             | - Phone QR Scan  |  | - National Stats   |
| - Calculate Fee  |  | - OIML R-76 Tests    |             | - Trust Badge    |  | - Overdue Tracker  |
| - Pay Fee & Track|  | - Live IoT Weight    |             | - Tamper Audit   |  | - Grievance Desk   |
| - Download Cert  |  | - Digital Signature  |             | - File Complaint |  | - Inspector Audits |
+------------------+  +----------------------+             +------------------+  +--------------------+
```

---

## 🚀 How to Run the Prototype

### Quick Launch (Windows)
Double-click `run.bat` in the project root:
```cmd
run.bat
```
Or execute via PowerShell / Command Prompt:
```cmd
cd "D:\SIH Problem Prototype"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### URLs to Access:
- **Main Portal Hub:** [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **ProductGuard AI (Batch Safety & Recall Scanner):** [http://127.0.0.1:8000/productguard](http://127.0.0.1:8000/productguard)
- **Trader Portal:** [http://127.0.0.1:8000/trader](http://127.0.0.1:8000/trader)
- **Inspector (LMO) Field App:** [http://127.0.0.1:8000/inspector](http://127.0.0.1:8000/inspector)
- **Central Ministry Dashboard:** [http://127.0.0.1:8000/admin](http://127.0.0.1:8000/admin)
- **Interactive OpenAPI (Swagger) Docs:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 📡 Live IoT Scale Simulator (Hardware Demo)
In a separate terminal window, start the virtual load cell simulator:
```cmd
python simulator/virtual_scale.py
```
This simulates standard test weights being placed on an electronic scale (1kg, 5kg, 10kg) and streams live packets over WebSockets directly into the Inspector's screen!

---

## 🎤 3-Minute Demonstration Walkthrough

1. **The Core Problem Solved (30 sec):**  
   *"When citizens buy groceries or a freight truck rolls onto a weighbridge, traditional lead wire seals are faked and paper certificates easily forged. **DISHA AI** digitizes the entire lifecycle."*
2. **Trader Registration & Fee Calculation (30 sec):**  
   *Open `/trader`.* Show how statutory fees are auto-calculated according to Legal Metrology 2011 slabs and the scale is geo-registered.
3. **The Anti-Fraud Inspector Field Test (60 sec):**  
   *Open `/inspector`.* 
   - Toggle **Demo Mode: Away (2.4km)**: Show how the system **blocks stamping** because the officer is not on-site.
   - Toggle **Demo Mode: On-Site (12m)**: The Geofence unlocks!
   - Click **"Capture from Load Cell"**: Show the live IoT weight appearing without manual typing.
   - Click **"Approve & Apply Digital Stamping Seal"**: Generates the signed certificate in real time!
4. **Instant Citizen Trust Badge & Live Scan (60 sec):**  
   *Scan the scale QR code with any smartphone camera.*
   - Point to the generated QR code or certificate.
   - Show the **Green Trust Badge**.
   - Click **"Verify Authenticity Live"**: Demonstrates the cryptographic HMAC-SHA256 signature verification.
   - Show the printable **Form-VIII Legal Certificate** with watermark.
