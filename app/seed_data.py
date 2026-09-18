from datetime import datetime, timedelta
from app.database import SessionLocal, Base, engine
from app import models
from app.crud import perform_inspection, create_instrument
from app.schemas import InstrumentCreate, InspectionCreate

def seed_database():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # Check if users already exist
        if db.query(models.User).first():
            print("Users already seeded. Checking ProductGuard AI data...")
            seed_productguard_data(db)
            db.commit()
            return

        print("Seeding initial users...")
        # 1. TRADERS
        trader1 = models.User(
            username="ramesh_trader",
            full_name="Ramesh Kumar Sharma",
            email="ramesh.store@gmail.com",
            phone="+91 98765 43210",
            role="TRADER",
            jurisdiction_district="Central Delhi",
            jurisdiction_state="Delhi"
        )
        trader2 = models.User(
            username="vikram_logistics",
            full_name="Vikram Singh Yadav",
            email="nh48.weighbridge@gmail.com",
            phone="+91 98111 22334",
            role="TRADER",
            jurisdiction_district="Gurugram",
            jurisdiction_state="Haryana"
        )
        trader3 = models.User(
            username="rajesh_jewels",
            full_name="Rajesh Verma",
            email="rajesh.tanishq@gmail.com",
            phone="+91 98223 34455",
            role="TRADER",
            jurisdiction_district="Central Delhi",
            jurisdiction_state="Delhi"
        )
        trader4 = models.User(
            username="harpreet_petrol",
            full_name="Harpreet Singh Anand",
            email="harpreet.iocl@gmail.com",
            phone="+91 98711 55667",
            role="TRADER",
            jurisdiction_district="South West Delhi",
            jurisdiction_state="Delhi"
        )
        trader5 = models.User(
            username="baldev_mandi",
            full_name="Baldev Raj Chadha",
            email="baldev.azadpur@gmail.com",
            phone="+91 98991 77889",
            role="TRADER",
            jurisdiction_district="North Delhi",
            jurisdiction_state="Delhi"
        )

        # 2. INSPECTOR
        inspector = models.User(
            username="lmo_verma",
            full_name="Devendra Kumar Verma",
            email="dk.verma.lmo@gov.in",
            phone="+91 94123 45678",
            role="INSPECTOR",
            badge_number="LMO-DL-07",
            jurisdiction_district="Central Delhi",
            jurisdiction_state="Delhi"
        )

        # 3. ADMIN
        admin = models.User(
            username="controller_metrology",
            full_name="Dr. Ananya Roy (IAS)",
            email="controller.lm@gov.in",
            phone="+91 11 2338 1234",
            role="ADMIN",
            badge_number="CLM-HQ-01",
            jurisdiction_district="National Capital Region",
            jurisdiction_state="Delhi"
        )

        db.add_all([trader1, trader2, trader3, trader4, trader5, inspector, admin])
        db.commit()
        db.refresh(trader1)
        db.refresh(trader2)
        db.refresh(trader3)
        db.refresh(trader4)
        db.refresh(trader5)
        db.refresh(inspector)

        print("Seeding instruments...")
        # Instrument 1: Sharma Kirana Store (Connaught Place - Verified)
        inst1_in = InstrumentCreate(
            owner_id=trader1.id,
            shop_name="Sharma Kirana & Departmental Store",
            trade_license_no="NDMC/TR/2024/9918",
            shop_address="Shop No 14, Shankar Market, Connaught Place",
            district="Central Delhi",
            state="Delhi",
            pincode="110001",
            latitude=28.6320,
            longitude=77.2180,
            instrument_type="COUNTER_SCALE_LE_50KG",
            brand_make="Essae-Teraoka DS-252",
            model_approval_number="IND/09/2021/418",
            serial_number="ES-2023-881920",
            max_capacity="30 kg",
            min_capacity="100 g",
            verification_interval="12 Months",
            accuracy_class="Class III",
            scheduled_date="Verified On-Site: 15 Jan 2026",
            contact_person="Ramesh Kumar Sharma",
            contact_phone="+91 98765 43210"
        )
        inst1 = create_instrument(db, inst1_in)

        # Perform verified inspection for Instrument 1 so a live QR & certificate already exists
        insp1_in = InspectionCreate(
            instrument_id=inst1.id,
            inspector_id=inspector.id,
            inspector_latitude=28.6321,
            inspector_longitude=77.2181,
            zero_setting_test=True,
            repeatability_test=True,
            eccentricity_corner_test=True,
            iot_reading_captured=5.000,
            max_error_observed=0.1,
            permissible_error_limit=1.0,
            photo_proof_path="/static/images/sample_scale.jpg",
            inspector_remarks="Scale verified with standard 5kg Class M1 test weight. Precision well within statutory permissible error limits under OIML R-76."
        )
        perform_inspection(db, insp1_in, base_url="http://127.0.0.1:8000")

        # Instrument 2: Platform Scale (Pending inspection - Connaught Place Godown)
        inst2_in = InstrumentCreate(
            owner_id=trader1.id,
            shop_name="Sharma Kirana Godown (Warehouse)",
            trade_license_no="NDMC/TR/2024/9919",
            shop_address="Godown 4B, Shankar Market, Connaught Place",
            district="Central Delhi",
            state="Delhi",
            pincode="110001",
            latitude=28.6320,
            longitude=77.2180,
            instrument_type="PLATFORM_SCALE_50_500KG",
            brand_make="Avery India Weightronix 200",
            model_approval_number="IND/11/2022/604",
            serial_number="AV-2024-554109",
            max_capacity="300 kg",
            min_capacity="2 kg",
            verification_interval="12 Months",
            accuracy_class="Class III",
            scheduled_date="Today, 10:30 AM - 11:30 AM",
            contact_person="Ramesh Kumar Sharma",
            contact_phone="+91 98765 43210"
        )
        inst2 = create_instrument(db, inst2_in)

        # Instrument 3: NH48 Highway Weighbridge (Gurugram Toll)
        inst3_in = InstrumentCreate(
            owner_id=trader2.id,
            shop_name="NH48 Toll Public Weighbridge",
            trade_license_no="MCG/COMM/WB/2023/11",
            shop_address="Near Kherki Daula Toll Plaza, NH-48",
            district="Gurugram",
            state="Haryana",
            pincode="122004",
            latitude=28.4110,
            longitude=76.9920,
            instrument_type="WEIGHBRIDGE_GT_50TON",
            brand_make="Sansui Heavy Duty Pitless Weighbridge",
            model_approval_number="IND/05/2020/190",
            serial_number="SAN-WB-100T-092",
            max_capacity="100 Tonnes",
            min_capacity="200 kg",
            verification_interval="12 Months",
            accuracy_class="Class IIII",
            scheduled_date="Today, 02:30 PM - 04:00 PM",
            contact_person="Vikram Singh Yadav",
            contact_phone="+91 98111 22334"
        )
        inst3 = create_instrument(db, inst3_in)

        # Instrument 4: Tanishq Gold & Diamond Jewellers (Karol Bagh)
        inst4_in = InstrumentCreate(
            owner_id=trader3.id,
            shop_name="Tanishq Gold & Diamond Jewellers",
            trade_license_no="MCD/KB/2024/7721",
            shop_address="2478/9 Ajmal Khan Road, Karol Bagh",
            district="Central Delhi",
            state="Delhi",
            pincode="110005",
            latitude=28.6517,
            longitude=77.1906,
            instrument_type="GOLD_PRECISION_SCALE",
            brand_make="Sartorius Cubis II Ultra-Precision Balance",
            model_approval_number="IND/04/2023/812",
            serial_number="SART-ME-2024-0041",
            max_capacity="600 g",
            min_capacity="0.001 g",
            verification_interval="12 Months",
            accuracy_class="Class II",
            scheduled_date="Tomorrow, 11:00 AM - 12:00 PM",
            contact_person="Rajesh Verma",
            contact_phone="+91 98223 34455"
        )
        inst4 = create_instrument(db, inst4_in)

        # Instrument 5: Indian Oil Corporation Fuel Dispenser (Moti Bagh)
        inst5_in = InstrumentCreate(
            owner_id=trader4.id,
            shop_name="Indian Oil Corporation Retail Outlet (Nozzle #4)",
            trade_license_no="DEL/EXP/PETROL/2023/88",
            shop_address="Ring Road Auto Service, Moti Bagh",
            district="South West Delhi",
            state="Delhi",
            pincode="110021",
            latitude=28.5878,
            longitude=77.1691,
            instrument_type="FUEL_DISPENSER_NOZZLE",
            brand_make="Midco Smart Multi-Product Fuel Dispenser",
            model_approval_number="IND/07/2021/334",
            serial_number="MIDCO-MPD-2023-902",
            max_capacity="50 L/min",
            min_capacity="5 L/min",
            verification_interval="12 Months",
            accuracy_class="Class 0.5",
            scheduled_date="Tomorrow, 03:30 PM - 04:30 PM",
            contact_person="Harpreet Singh Anand",
            contact_phone="+91 98711 55667"
        )
        inst5 = create_instrument(db, inst5_in)

        # Instrument 6: Azadpur Mandi Heavy Commercial Platform (Verified)
        inst6_in = InstrumentCreate(
            owner_id=trader5.id,
            shop_name="Azadpur APMC Fruit & Veg Wholesale Mandi (Platform #12)",
            trade_license_no="APMC/DEL/2022/4119",
            shop_address="Shed 12, Gate 3, Azadpur Mandi",
            district="North Delhi",
            state="Delhi",
            pincode="110033",
            latitude=28.7154,
            longitude=77.1782,
            instrument_type="PLATFORM_SCALE_500_5000KG",
            brand_make="Phoenix Heavy Commercial Platform",
            model_approval_number="IND/02/2022/105",
            serial_number="PHOEN-PF-2024-1108",
            max_capacity="1000 kg",
            min_capacity="5 kg",
            verification_interval="12 Months",
            accuracy_class="Class III",
            scheduled_date="Verified On-Site: 02 Feb 2026",
            contact_person="Baldev Raj Chadha",
            contact_phone="+91 98991 77889"
        )
        inst6 = create_instrument(db, inst6_in)

        # Perform verified inspection for Instrument 6
        insp6_in = InspectionCreate(
            instrument_id=inst6.id,
            inspector_id=inspector.id,
            inspector_latitude=28.7155,
            inspector_longitude=77.1783,
            zero_setting_test=True,
            repeatability_test=True,
            eccentricity_corner_test=True,
            iot_reading_captured=20.000,
            max_error_observed=0.2,
            permissible_error_limit=2.0,
            photo_proof_path="/static/images/sample_scale.jpg",
            inspector_remarks="Mandi heavy platform scale tested with 20kg Class M1 test weight. Corner and eccentricity tests passed under Section 24 of Legal Metrology Act."
        )
        perform_inspection(db, insp6_in, base_url="http://127.0.0.1:8000")

        # Seed citizen complaints
        comp1 = models.Complaint(
            complaint_id="GRIEV-2026-1049",
            instrument_id=inst1.id,
            complainant_name="Amitabh Saxena",
            complainant_phone="+91 99887 76655",
            complainant_email="amitabh.delhi@gmail.com",
            complaint_type="Suspicion of Under-weighing",
            description="Purchased 2kg lentils, weighed 1.85kg when checked on another domestic scale. Requesting audit of shop scale.",
            status="RESOLVED",
            admin_notes="Officer Verma audited on-site on 15 Jan. Scale recalibrated and stamped genuine."
        )
        comp2 = models.Complaint(
            complaint_id="GRIEV-2026-1052",
            instrument_id=inst3.id,
            complainant_name="Surender Kataria (Freight Driver)",
            complainant_phone="+91 97182 34490",
            complainant_email="surender.trucking@gmail.com",
            complaint_type="Weighbridge Discrepancy",
            description="Gross weight difference of 350 kg observed between Jaipur toll weighbridge and NH48 Gurugram weighbridge.",
            status="OPEN",
            admin_notes="Scheduled for immediate statutory calibration test today by LMO-DL-07."
        )
        db.add_all([comp1, comp2])

        # Seed Nationally Approved Models (RRSL Evaluated)
        if not db.query(models.ModelApproval).first():
            m1 = models.ModelApproval(
                approval_number="IND/09/2021/418",
                manufacturer_name="Essae-Teraoka Private Limited",
                brand_name="Essae DS-252",
                instrument_type="Electronic Counter Scale",
                accuracy_class="Class III",
                max_capacity="30 kg",
                rrsl_testing_lab="RRSL Faridabad (Govt of India)",
                oiml_recommendation="OIML R-76-1:2006",
                validity_years=10,
                status="APPROVED"
            )
            m2 = models.ModelApproval(
                approval_number="IND/11/2022/604",
                manufacturer_name="Avery India Limited",
                brand_name="Avery Weightronix 200",
                instrument_type="Industrial Platform Scale",
                accuracy_class="Class III",
                max_capacity="300 kg",
                rrsl_testing_lab="RRSL Bengaluru (Govt of India)",
                oiml_recommendation="OIML R-76-1:2006",
                validity_years=10,
                status="APPROVED"
            )
            m3 = models.ModelApproval(
                approval_number="IND/05/2020/190",
                manufacturer_name="Sansui Heavy Electronics Pvt Ltd",
                brand_name="Sansui Pitless Weighbridge",
                instrument_type="Electronic Weighbridge",
                accuracy_class="Class IIII",
                max_capacity="100 Tonnes",
                rrsl_testing_lab="RRSL Ahmedabad (Govt of India)",
                oiml_recommendation="OIML R-76-1:2006",
                validity_years=10,
                status="APPROVED"
            )
            m4 = models.ModelApproval(
                approval_number="IND/04/2023/812",
                manufacturer_name="Sartorius India Private Limited",
                brand_name="Sartorius Cubis II Ultra-Precision",
                instrument_type="High-Precision Balance",
                accuracy_class="Class II",
                max_capacity="600 g",
                rrsl_testing_lab="National Physical Laboratory (NPL New Delhi)",
                oiml_recommendation="OIML R-76-1:2006",
                validity_years=10,
                status="APPROVED"
            )
            m5 = models.ModelApproval(
                approval_number="IND/07/2021/334",
                manufacturer_name="Midco Limited",
                brand_name="Midco Smart Multi-Product Dispenser",
                instrument_type="Automatic Fuel Dispenser",
                accuracy_class="Class 0.5",
                max_capacity="50 L/min",
                rrsl_testing_lab="RRSL Faridabad (Govt of India)",
                oiml_recommendation="OIML R-117-1:2019",
                validity_years=10,
                status="APPROVED"
            )
            m6 = models.ModelApproval(
                approval_number="IND/02/2022/105",
                manufacturer_name="Phoenix Scales & Automation",
                brand_name="Phoenix Heavy Commercial Platform",
                instrument_type="Industrial Platform Scale",
                accuracy_class="Class III",
                max_capacity="1000 kg",
                rrsl_testing_lab="RRSL Ahmedabad (Govt of India)",
                oiml_recommendation="OIML R-76-1:2006",
                validity_years=10,
                status="APPROVED"
            )
            db.add_all([m1, m2, m3, m4, m5, m6])
            db.commit()
            print("Seed data successfully populated with 6 instruments, model approvals, and inspection history!")

        # Always ensure ProductGuard AI data is seeded
        seed_productguard_data(db)
        db.commit()

    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

def seed_productguard_data(db, force_refresh: bool = False):
    # If already seeded with all sectors, skip
    if not force_refresh and db.query(models.PGProduct).count() >= 15:
        print("ProductGuard AI data already fully seeded. Skipping...")
        return

    print("Re-creating and seeding comprehensive ProductGuard AI data (Health, Baby Products, Food)...")
    try:
        models.PGInventory.__table__.drop(bind=engine, checkfirst=True)
        models.PGGrievance.__table__.drop(bind=engine, checkfirst=True)
        models.PGBatch.__table__.drop(bind=engine, checkfirst=True)
        models.PGProduct.__table__.drop(bind=engine, checkfirst=True)
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"Table recreation notice: {e}")

    now = datetime.utcnow()

    # =========================================================================
    # SECTOR 1: HEALTH SECTOR (MEDICINES, DRUGS & PHARMACEUTICALS)
    # =========================================================================

    # 1. Coldrif Pediatric Cough Syrup (Critical Toxic Recall)
    p_coldrif = models.PGProduct(
        barcode="8904032198765",
        brand_name="Sreshta Pharma",
        product_name="Coldrif Antitussive Pediatric Cough Syrup (100ml)",
        sector="HEALTH_PHARMA",
        category="Medicine",
        sub_category="Pediatric Cough Formulation",
        fssai_license="CDSCO-DL-MH-8892 (Drug Mfg Lic Form 25)",
        net_quantity="100 ml",
        mrp=115.0,
        image_url="/static/products/coldrif_syrup.png"
    )
    db.add(p_coldrif)
    db.flush()

    b_coldrif = models.PGBatch(
        product_id=p_coldrif.id,
        batch_number="SR-13",
        mfg_date=now - timedelta(days=50),
        expiry_date=now + timedelta(days=500), # Printed expiry 2027
        status="RECALLED",
        is_recalled=True,
        hazard_level="CRITICAL",
        regulatory_authority="CDSCO & Maharashtra FDA (IAS Tukaram Mundhe Special Task Force)",
        lab_test_report_id="MH-FDA-HAZ-2026-89",
        recall_reason="CRITICAL TOXIC SOLVENT ALERT: Batch SR-13 chemical gas chromatography confirmed 1.4% Diethylene Glycol (DEG) / Toxic Industrial Solvent exceeding lethal pediatric threshold. CDSCO National Alert active. Immediate seizure ordered under Sec 26 Drugs & Cosmetics Act.",
        lab_test_summary="FAILED SAFETY AUDIT. High concentration of toxic diethylene glycol (DEG) solvent contaminant detected. Extreme risk of acute kidney injury in children. Confiscation and legal FIR registered.",
        storage_temperature="Store below 25°C. Protect from light.",
        adverse_events_count=4
    )
    db.add(b_coldrif)

    # 2. Azicip-500 Azithromycin Tablets (Safe & Genuine)
    p_azithro = models.PGProduct(
        barcode="8901117012011",
        brand_name="Cipla Healthcare",
        product_name="Azicip-500 Azithromycin Tablets IP 500mg",
        sector="HEALTH_PHARMA",
        category="Medicine",
        sub_category="Broad-Spectrum Macrolide Antibiotic",
        fssai_license="CDSCO-MFG-HP-4190 (Drug Mfg Lic Form 28)",
        net_quantity="Strip of 3 Tablets",
        mrp=71.50
    )
    db.add(p_azithro)
    db.flush()

    b_azithro_safe = models.PGBatch(
        product_id=p_azithro.id,
        batch_number="AZ-8021",
        mfg_date=now - timedelta(days=60),
        expiry_date=now + timedelta(days=420),
        status="SAFE",
        is_recalled=False,
        hazard_level="NONE",
        regulatory_authority="CDSCO Central Drug Testing Laboratory (CDTL Mumbai)",
        lab_test_report_id="CDTL-MUM-2026-5541",
        lab_test_summary="HPLC Assay: 99.8% Azithromycin Dihydrate (IP standard: 95.0% - 105.0%). Disintegration time 5.8 mins. Heavy metals, organic impurities & microbiological limits compliant with Indian Pharmacopoeia 2022.",
        storage_temperature="Store below 30°C. Protect from moisture.",
        adverse_events_count=0
    )
    # 3. Spurious Azicip Batch (Counterfeit Drug Alert)
    b_azithro_fake = models.PGBatch(
        product_id=p_azithro.id,
        batch_number="AZ-8029",
        mfg_date=now - timedelta(days=90),
        expiry_date=now + timedelta(days=360),
        status="RECALLED",
        is_recalled=True,
        hazard_level="CRITICAL",
        regulatory_authority="CDSCO & Maharashtra FDA Flying Squad Raigad",
        lab_test_report_id="CDSCO-NSQ-2026-118",
        recall_reason="SPURIOUS & COUNTERFEIT DRUG ALERT: Batch AZ-8029 confirmed as an illegal counterfeit imitation seized during Raigad factory raid. HPLC assay revealed 0% Active Pharmaceutical Ingredient (API); formulation consists of chalk, talc and starch binders. FIR registered.",
        lab_test_summary="NOT OF STANDARD QUALITY (NSQ) - Falsified Drug. Zero therapeutic efficacy. Threat to life in acute bacterial infections. Confiscate immediately.",
        storage_temperature="CONFISCATED STOCK",
        adverse_events_count=7
    )
    db.add_all([b_azithro_safe, b_azithro_fake])

    # 4. Calpol Paediatric Suspension (Safe)
    p_calpol = models.PGProduct(
        barcode="8901034015522",
        brand_name="GlaxoSmithKline (GSK)",
        product_name="Calpol Paediatric Oral Suspension 250mg/5ml",
        sector="HEALTH_PHARMA",
        category="Medicine",
        sub_category="Paediatric Antipyretic & Analgesic",
        fssai_license="CDSCO-MFG-AP-2010 (Form 25 Lic)",
        net_quantity="60 ml",
        mrp=48.20
    )
    db.add(p_calpol)
    db.flush()

    b_calpol = models.PGBatch(
        product_id=p_calpol.id,
        batch_number="CAL-991",
        mfg_date=now - timedelta(days=30),
        expiry_date=now + timedelta(days=330),
        status="SAFE",
        is_recalled=False,
        hazard_level="NONE",
        regulatory_authority="Indian Pharmacopoeia Commission (IPC Ghaziabad)",
        lab_test_report_id="IPC-GZB-2026-8820",
        lab_test_summary="Paracetamol active content: 249.2 mg/5ml. Screened for DEG and Ethylene Glycol solvent contaminants: NOT DETECTED (Below 0.001% LOD). Conforms to IP 2022 Monograph.",
        storage_temperature="Store below 25°C. Do not freeze.",
        adverse_events_count=0
    )
    db.add(b_calpol)

    # 5. Monocef 1g Ceftriaxone Injection (Expiring Soon - 48h)
    p_monocef = models.PGProduct(
        barcode="8901248003112",
        brand_name="Aristo Pharmaceuticals",
        product_name="Monocef 1g Sterile Ceftriaxone Injection IP",
        sector="HEALTH_PHARMA",
        category="Medicine",
        sub_category="Hospital Cephalosporin Injectable",
        fssai_license="CDSCO-MFG-MP-1044 (Form 28)",
        net_quantity="1 Vial with SWFI",
        mrp=65.0
    )
    db.add(p_monocef)
    db.flush()

    b_monocef = models.PGBatch(
        product_id=p_monocef.id,
        batch_number="MC-4402",
        mfg_date=now - timedelta(days=720),
        expiry_date=now + timedelta(days=2), # Expiring in 48 hours!
        status="EXPIRING_SOON",
        is_recalled=False,
        hazard_level="MODERATE",
        regulatory_authority="State Drug Control Administration (FDA Delhi)",
        lab_test_report_id="DCA-DEL-2026-4011",
        lab_test_summary="Sterile at release. Rapid hospital inventory warning: Shelf-life expires in 48 hours. Risk of reconstitution degradation. Recommend immediate distributor return or emergency ICU allocation.",
        storage_temperature="Store in cool dry place below 25°C.",
        adverse_events_count=0
    )
    db.add(b_monocef)

    # 6. Lantus Insulin Glargine (Cold-Chain Transit Failure Recall)
    p_lantus = models.PGProduct(
        barcode="8901043009941",
        brand_name="Sanofi India",
        product_name="Lantus 100 IU/ml Insulin Glargine Cartridge",
        sector="HEALTH_PHARMA",
        category="Medicine",
        sub_category="Recombinant Long-Acting Human Insulin",
        fssai_license="CDSCO-IMPORT-BIO-2291",
        net_quantity="3 ml Cartridge",
        mrp=680.0
    )
    db.add(p_lantus)
    db.flush()

    b_lantus = models.PGBatch(
        product_id=p_lantus.id,
        batch_number="LT-1108",
        mfg_date=now - timedelta(days=40),
        expiry_date=now + timedelta(days=320),
        status="RECALLED",
        is_recalled=True,
        hazard_level="CRITICAL",
        regulatory_authority="Maharashtra FDA Drug Vigilance Directorate",
        lab_test_report_id="MH-FDA-COLD-2026-72",
        recall_reason="COLD-CHAIN FAILURE RECALL: Central transit temperature loggers revealed refrigeration compressor failure during interstate highway transport (exceeded 28°C for 42 hours). Denatured insulin protein with loss of glycemic control. Risk of diabetic ketoacidosis.",
        lab_test_summary="Protein chromatography confirms thermal denaturation and peptide degradation. Bio-potency dropped below 60%. Quarantined for safe biological destruction.",
        storage_temperature="Requires strict 2°C - 8°C (VIOLATED)",
        adverse_events_count=5
    )
    db.add(b_lantus)

    # 7. Pan-40 Tablets (Safe)
    p_pan = models.PGProduct(
        barcode="8901083011234",
        brand_name="Alkem Laboratories",
        product_name="Pan-40 Pantoprazole Gastro-Resistant Tablets IP",
        sector="HEALTH_PHARMA",
        category="Medicine",
        sub_category="Gastrointestinal PPI",
        fssai_license="CDSCO-MFG-HP-9901",
        net_quantity="Strip of 15 Tablets",
        mrp=155.0
    )
    db.add(p_pan)
    db.flush()

    b_pan = models.PGBatch(
        product_id=p_pan.id,
        batch_number="PAN-3031",
        mfg_date=now - timedelta(days=45),
        expiry_date=now + timedelta(days=500),
        status="SAFE",
        is_recalled=False,
        hazard_level="NONE",
        regulatory_authority="CDSCO Central Drugs Testing Lab (CDTL Kolkata)",
        lab_test_report_id="CDTL-KOL-2026-3190",
        lab_test_summary="Acid-resistance test passed (>98% intact in 0.1N HCl). Drug release at pH 6.8 buffer: 99.4%. Excipient compatibility certified.",
        storage_temperature="Ambient (<25°C)",
        adverse_events_count=0
    )
    db.add(b_pan)


    # =========================================================================
    # SECTOR 2: BABY PRODUCTS & INFANT NUTRITION (CONSUMED BY BABIES)
    # =========================================================================

    # 8. Nestlé Lactogen Infant Formula Stage 1 (Safe)
    p_lactogen = models.PGProduct(
        barcode="8901058852331",
        brand_name="Nestlé India",
        product_name="Nestlé Lactogen Infant Formula Stage 1 (0-6 Months)",
        sector="BABY_PRODUCTS",
        category="Baby Food",
        sub_category="Infant Milk Substitute",
        fssai_license="10012011000168 (FSSAI Infant Food Regulations)",
        net_quantity="400 g Bag-in-Box",
        mrp=450.0,
        image_url="/static/products/lactogen.png"
    )
    db.add(p_lactogen)
    db.flush()

    b_lactogen = models.PGBatch(
        product_id=p_lactogen.id,
        batch_number="LAC-4109",
        mfg_date=now - timedelta(days=25),
        expiry_date=now + timedelta(days=340),
        status="SAFE",
        is_recalled=False,
        hazard_level="NONE",
        regulatory_authority="FSSAI National Centre for Infant Food Quality (CFTRI Mysore)",
        lab_test_report_id="CFTRI-INF-2026-1104",
        lab_test_summary="Screened negative for Cronobacter sakazakii & Salmonella. Whey:casein protein ratio 60:40 compliant. Toxic heavy metals (Lead, Cadmium, Arsenic): Below Detection Limit. Zero added sugars.",
        storage_temperature="Cool, dry, airtight container",
        adverse_events_count=0
    )
    db.add(b_lactogen)

    # 9. Nestlé Cerelac Wheat-Apple Baby Cereal (Excess Added Sugar Recall)
    p_cerelac = models.PGProduct(
        barcode="8901058863214",
        brand_name="Nestlé Nutrition",
        product_name="Nestlé Cerelac Wheat-Apple Baby Cereal with Milk (6+ Months)",
        sector="BABY_PRODUCTS",
        category="Baby Food",
        sub_category="Infant Complementary Weaning Food",
        fssai_license="10012011000168",
        net_quantity="300 g Refill Pack",
        mrp=280.0,
        image_url="/static/products/cerelac.png"
    )
    db.add(p_cerelac)
    db.flush()

    b_cerelac = models.PGBatch(
        product_id=p_cerelac.id,
        batch_number="CER-892",
        mfg_date=now - timedelta(days=35),
        expiry_date=now + timedelta(days=330),
        status="RECALLED",
        is_recalled=True,
        hazard_level="CRITICAL",
        regulatory_authority="FSSAI Central Expert Task Force on Infant Foods & Maharashtra FDA",
        lab_test_report_id="FSSAI-INF-2026-899",
        recall_reason="REGULATORY RECALL & REFORMULATION ORDER: FSSAI surprise laboratory audit detected 2.7g of hidden added sucrose/maltodextrin per serving, violating Section 5(a) of Updated Infant Nutrition Standards 2026. Risk of early infant metabolic disorder and tooth bud decay. Immediate shelf clearance ordered.",
        lab_test_summary="NON-COMPLIANT ADDED SUGAR CONTENT. Laboratory analysis showed unpermitted added sucrose in infant complementary cereal. Quarantined across all retail shelves.",
        storage_temperature="Store in cool, dry place.",
        adverse_events_count=12
    )
    db.add(b_cerelac)

    # 10. Woodward's Gripe Water (Safe)
    p_gripe = models.PGProduct(
        barcode="8901425001221",
        brand_name="Woodward's (TTK Healthcare)",
        product_name="Woodward's Gripe Water for Infants (130ml)",
        sector="BABY_PRODUCTS",
        category="Baby Care",
        sub_category="Pediatric Digestive Formulation",
        fssai_license="AYUSH-LIC-TN-4180",
        net_quantity="130 ml Bottle",
        mrp=65.0
    )
    db.add(p_gripe)
    db.flush()

    b_gripe_safe = models.PGBatch(
        product_id=p_gripe.id,
        batch_number="WD-2041",
        mfg_date=now - timedelta(days=20),
        expiry_date=now + timedelta(days=340),
        status="SAFE",
        is_recalled=False,
        hazard_level="NONE",
        regulatory_authority="Ministry of Ayush & Central Drug Standard Directorate",
        lab_test_report_id="AYUSH-LAB-2026-610",
        lab_test_summary="Zero alcohol content. Tested negative for synthetic sedatives, parabens and heavy metals. Dill seed oil & sodium bicarbonate potency 100.4%. Safe for infants 1 to 12 months.",
        storage_temperature="Ambient (<25°C)",
        adverse_events_count=0
    )
    # 11. Woodward's Contaminated Batch (Microbial Fungal Recall)
    b_gripe_bad = models.PGBatch(
        product_id=p_gripe.id,
        batch_number="WD-2049",
        mfg_date=now - timedelta(days=45),
        expiry_date=now + timedelta(days=315),
        status="RECALLED",
        is_recalled=True,
        hazard_level="CRITICAL",
        regulatory_authority="Maharashtra FDA Thane Division (Commissioner IAS Tukaram Mundhe Raid)",
        lab_test_report_id="MH-FDA-INF-2026-302",
        recall_reason="FUNGAL SPORE CONTAMINATION: Microbiological plating confirmed Cladosporium fungal colony growth and non-permitted synthetic benzoic acid preservative in Batch WD-2049. 14 infant gastrointestinal irritation complaints logged. Seizure notice active.",
        lab_test_summary="FAILED MICROBIAL STERILITY. Viable fungal colonies present. High health hazard for infant digestive tract. Prohibited from sale.",
        storage_temperature="CONFISCATED STOCK",
        adverse_events_count=14
    )
    db.add_all([b_gripe_safe, b_gripe_bad])

    # 12. D-Well Baby Vitamin D3 Drops (Safe)
    p_vitd = models.PGProduct(
        barcode="8901117228801",
        brand_name="Sun Pharma Consumer Healthcare",
        product_name="D-Well Baby Vitamin D3 Pediatric Oral Drops (800 IU/ml)",
        sector="BABY_PRODUCTS",
        category="Baby Care",
        sub_category="Neonatal & Pediatric Nutritional Drops",
        fssai_license="CDSCO-MFG-GUJ-1192",
        net_quantity="15 ml Dropper Bottle",
        mrp=135.0
    )
    db.add(p_vitd)
    db.flush()

    b_vitd = models.PGBatch(
        product_id=p_vitd.id,
        batch_number="VD-5520",
        mfg_date=now - timedelta(days=15),
        expiry_date=now + timedelta(days=350),
        status="SAFE",
        is_recalled=False,
        hazard_level="NONE",
        regulatory_authority="CDSCO Central Drugs Laboratory (Kasauli)",
        lab_test_report_id="CDL-KAS-2026-4410",
        lab_test_summary="Calibrated dropper delivers exact 400 IU per 0.5ml. Cholecalciferol active assay: 101.5%. Screened free of microbial contamination. Safe for neonatal administration.",
        storage_temperature="Store between 15°C - 25°C. Protect from light.",
        adverse_events_count=0
    )
    db.add(b_vitd)

    # 13. Little's Baby Pure Water Wipes (Expiring Soon - 3 days)
    p_wipes = models.PGProduct(
        barcode="8901233008910",
        brand_name="Piramal Healthcare",
        product_name="Little's Soft & Gentle Baby Pure Water Wipes",
        sector="BABY_PRODUCTS",
        category="Baby Care",
        sub_category="Infant Skin & Hygiene",
        fssai_license="FDA-COS-LIC-MH-771",
        net_quantity="Pack of 80 Wipes",
        mrp=190.0
    )
    db.add(p_wipes)
    db.flush()

    b_wipes = models.PGBatch(
        product_id=p_wipes.id,
        batch_number="LW-712",
        mfg_date=now - timedelta(days=360),
        expiry_date=now + timedelta(days=3), # 3 days remaining!
        status="EXPIRING_SOON",
        is_recalled=False,
        hazard_level="MODERATE",
        regulatory_authority="State FDA Cosmetics & Pediatric Division",
        lab_test_report_id="FDA-COS-2026-118",
        lab_test_summary="Natural preservative breakdown imminent. Approaching 72-hour moisture desiccation threshold. Risk of bacterial colonization once seal is unlatched. Recommended for clearance markdown.",
        storage_temperature="Keep lid tightly closed.",
        adverse_events_count=0
    )
    db.add(b_wipes)

    # 14. Sebamed Baby Gentle Wash (Safe)
    p_sebamed = models.PGProduct(
        barcode="4103040114002",
        brand_name="Sebamed Germany / USV India",
        product_name="Sebamed Baby Gentle Wash Extra Soft (200ml)",
        sector="BABY_PRODUCTS",
        category="Baby Care",
        sub_category="Pediatric Dermatology Cleanser",
        fssai_license="CDSCO-COS-IMPORT-4011",
        net_quantity="200 ml Bottle",
        mrp=460.0
    )
    db.add(p_sebamed)
    db.flush()

    b_sebamed = models.PGBatch(
        product_id=p_sebamed.id,
        batch_number="SBM-901",
        mfg_date=now - timedelta(days=40),
        expiry_date=now + timedelta(days=500),
        status="SAFE",
        is_recalled=False,
        hazard_level="NONE",
        regulatory_authority="FSSAI & CDSCO Cosmetic Safety Division",
        lab_test_report_id="CDSCO-COS-2026-902",
        lab_test_summary="pH 5.5 clinically verified (protects infant skin acid mantle). Free of parabens, formaldehyde, and phthalates. 100% soap-free hypoallergenic formulation passed.",
        storage_temperature="Store at room temperature",
        adverse_events_count=0
    )
    db.add(b_sebamed)


    # =========================================================================
    # SECTOR 3: FOOD & DAIRY CONSUMABLES (EXISTING CORE DATASETS)
    # =========================================================================

    # 15. Amul Taaza Milk (Safe)
    p_amul = models.PGProduct(
        barcode="8901262010053",
        brand_name="Amul",
        product_name="Taaza Fresh Toned Milk (1 Litre Tetra)",
        sector="FOOD_CONSUMABLES",
        category="Dairy",
        sub_category="Pasteurized Toned Milk",
        fssai_license="10012021000071",
        net_quantity="1000 ml",
        mrp=54.0,
        image_url="/static/products/amul_taaza.png"
    )
    db.add(p_amul)
    db.flush()

    b_amul = models.PGBatch(
        product_id=p_amul.id,
        batch_number="AM-2409",
        mfg_date=now - timedelta(days=15),
        expiry_date=now + timedelta(days=30),
        status="SAFE",
        is_recalled=False,
        hazard_level="NONE",
        regulatory_authority="FSSAI Central Food Safety Lab & Gujarat Food & Drug Control",
        lab_test_report_id="FSSAI-NDTL-2026-9812",
        lab_test_summary="Passed FSSAI Micro-biology & Milk Adulterant screening. Negative for synthetic urea, detergent, starch, and melamine. SNF: 8.5%, Fat: 3.0% (Compliant).",
        storage_temperature="Ambient before opening, refrigerate after opening",
        adverse_events_count=0
    )
    db.add(b_amul)

    # 16. Harvest Gold Bread (Expiring Tomorrow)
    p_bread = models.PGProduct(
        barcode="8906012345678",
        brand_name="Harvest Gold",
        product_name="100% Atta Whole Wheat Bread",
        sector="FOOD_CONSUMABLES",
        category="Bakery",
        sub_category="Fresh Sliced Bread",
        fssai_license="10014011001895",
        net_quantity="400 g",
        mrp=45.0,
        image_url="/static/products/harvest_bread.png"
    )
    db.add(p_bread)
    db.flush()

    b_bread = models.PGBatch(
        product_id=p_bread.id,
        batch_number="HB-1102",
        mfg_date=now - timedelta(days=5),
        expiry_date=now + timedelta(days=1), # Tomorrow!
        status="EXPIRING_SOON",
        is_recalled=False,
        hazard_level="MODERATE",
        regulatory_authority="FSSAI Food Safety Audit Wing",
        lab_test_report_id="CFTRI-MYS-2026-3341",
        lab_test_summary="Standard microbiological compliance at dispatch. Approaching maximum recommended moisture/yeast shelf-life threshold. Recommend prompt consumption within 24h or clearance discount.",
        storage_temperature="Keep in cool dry breadbox",
        adverse_events_count=0
    )
    db.add(b_bread)

    # 17. Fortune Mustard Oil (Safe & Recalled Batches)
    p_oil = models.PGProduct(
        barcode="8906007281014",
        brand_name="Fortune",
        product_name="Kachi Ghani Pure Mustard Oil",
        sector="FOOD_CONSUMABLES",
        category="Edible Oil",
        sub_category="Cold-Pressed Mustard Oil",
        fssai_license="10013021000853",
        net_quantity="1 Litre Bottle",
        mrp=165.0
    )
    db.add(p_oil)
    db.flush()

    b_oil_safe = models.PGBatch(
        product_id=p_oil.id,
        batch_number="FT-9021",
        mfg_date=now - timedelta(days=20),
        expiry_date=now + timedelta(days=250),
        status="SAFE",
        is_recalled=False,
        hazard_level="NONE",
        regulatory_authority="FSSAI Central Oil Testing Lab",
        lab_test_report_id="FSSAI-OIL-2026-104",
        lab_test_summary="Pungency standard (Allyl isothiocyanate: 0.31%). Zero Argemone or mineral oil adulteration detected.",
        storage_temperature="Ambient",
        adverse_events_count=0
    )
    b_oil_bad = models.PGBatch(
        product_id=p_oil.id,
        batch_number="FT-9022",
        mfg_date=now - timedelta(days=60),
        expiry_date=now + timedelta(days=210),
        status="RECALLED",
        is_recalled=True,
        hazard_level="CRITICAL",
        regulatory_authority="Maharashtra FDA Vigilance Wing",
        lab_test_report_id="MH-FDA-OIL-2026-441",
        recall_reason="FDA SEIZURE NOTICE: Suspected synthetic colour adulteration and Argemone seed oil contamination. Seizure initiated in 8 districts.",
        lab_test_summary="Adulteration with non-permitted synthetic dyes and Argemone oil traces. Unsafe for human consumption.",
        storage_temperature="CONFISCATED STOCK",
        adverse_events_count=3
    )
    db.add_all([b_oil_safe, b_oil_bad])

    # 18. Mother Dairy Dahi (Safe & Expired Batches)
    p_dahi = models.PGProduct(
        barcode="8901648001021",
        brand_name="Mother Dairy",
        product_name="Classic Dahi Pouch",
        sector="FOOD_CONSUMABLES",
        category="Dairy",
        sub_category="Fermented Dairy Curd",
        fssai_license="10014011002630",
        net_quantity="400 g Pouch",
        mrp=35.0
    )
    db.add(p_dahi)
    db.flush()

    b_dahi_safe = models.PGBatch(
        product_id=p_dahi.id,
        batch_number="MD-5510",
        mfg_date=now - timedelta(days=3),
        expiry_date=now + timedelta(days=9),
        status="SAFE",
        is_recalled=False,
        hazard_level="NONE",
        regulatory_authority="FSSAI Quality Directorate",
        lab_test_report_id="NDDB-LAB-2026-778",
        lab_test_summary="Total bacterial count compliant. Free of artificial thickeners or starch.",
        storage_temperature="Refrigerated (4°C)",
        adverse_events_count=0
    )
    b_dahi_expired = models.PGBatch(
        product_id=p_dahi.id,
        batch_number="MD-5490",
        mfg_date=now - timedelta(days=20),
        expiry_date=now - timedelta(days=4), # Expired 4 days ago
        status="EXPIRED",
        is_recalled=False,
        hazard_level="HIGH",
        regulatory_authority="FSSAI Quality Directorate",
        lab_test_report_id="NDDB-LAB-2026-612",
        lab_test_summary="Expired shelf life. High lactic acidity and microbial overgrowth risk.",
        storage_temperature="Refrigerated (4°C)",
        adverse_events_count=1
    )
    db.add_all([b_dahi_safe, b_dahi_expired])
    db.flush()


    # =========================================================================
    # RETAILER & PHARMACY SHELF INVENTORY (MULTI-STORE REALISTIC STOCK)
    # =========================================================================
    inventories = [
        # Hospital / Pharmacy stocks
        models.PGInventory(batch_id=b_coldrif.id, store_name="City Apollo Pharmacy", store_location="Andheri East, Mumbai", stock_quantity=14, marked_for_removal=False),
        models.PGInventory(batch_id=b_azithro_safe.id, store_name="City Apollo Pharmacy", store_location="Andheri East, Mumbai", stock_quantity=120, marked_for_removal=False),
        models.PGInventory(batch_id=b_azithro_fake.id, store_name="Shree Ram Medicos", store_location="Sector 15, Faridabad", stock_quantity=22, marked_for_removal=False),
        models.PGInventory(batch_id=b_monocef.id, store_name="Maxcare Hospital Chemist", store_location="South Ext, New Delhi", stock_quantity=18, marked_for_removal=False),
        models.PGInventory(batch_id=b_lantus.id, store_name="City Lifeline Hospital Pharmacy", store_location="FC Road, Pune", stock_quantity=9, marked_for_removal=True),
        models.PGInventory(batch_id=b_calpol.id, store_name="MedPlus Pharmacy", store_location="HSR Layout, Bengaluru", stock_quantity=65, marked_for_removal=False),

        # Baby Stores & Supermarket stocks
        models.PGInventory(batch_id=b_lactogen.id, store_name="FirstCry Infant Superstore", store_location="Indiranagar, Bengaluru", stock_quantity=40, marked_for_removal=False),
        models.PGInventory(batch_id=b_cerelac.id, store_name="Krishna Supermarket & Kirana", store_location="Sector 18, Noida", stock_quantity=16, marked_for_removal=False),
        models.PGInventory(batch_id=b_gripe_bad.id, store_name="Krishna Supermarket & Kirana", store_location="Sector 18, Noida", stock_quantity=12, marked_for_removal=False),
        models.PGInventory(batch_id=b_wipes.id, store_name="Mothercare Flagship", store_location="Select Citywalk, New Delhi", stock_quantity=8, marked_for_removal=False),
        models.PGInventory(batch_id=b_sebamed.id, store_name="FirstCry Infant Superstore", store_location="Indiranagar, Bengaluru", stock_quantity=25, marked_for_removal=False),

        # Grocery stocks
        models.PGInventory(batch_id=b_amul.id, store_name="Krishna Supermarket & Kirana", store_location="Sector 18, Noida", stock_quantity=48, marked_for_removal=False),
        models.PGInventory(batch_id=b_bread.id, store_name="Krishna Supermarket & Kirana", store_location="Sector 18, Noida", stock_quantity=12, marked_for_removal=False),
        models.PGInventory(batch_id=b_oil_bad.id, store_name="Aapka Bazaar Hyperstore", store_location="Connaught Place, New Delhi", stock_quantity=15, marked_for_removal=True),
        models.PGInventory(batch_id=b_dahi_expired.id, store_name="Laxmi Daily Needs", store_location="Andheri West, Mumbai", stock_quantity=6, marked_for_removal=False)
    ]
    db.add_all(inventories)


    # =========================================================================
    # PRE-SEEDED CONSUMER GRIEVANCES WITH MULTI-STAGE PIPELINES (STAGES 1 TO 4)
    # =========================================================================
    g1 = models.PGGrievance(
        docket_number="PG-GRIEV-2026-1082",
        batch_number="SR-13",
        product_name="Coldrif Antitussive Pediatric Cough Syrup",
        sector="HEALTH_PHARMA",
        shop_name="Krishna Medical & Chemists",
        shop_location="Andheri East, Mumbai",
        latitude=19.1136,
        longitude=72.8697,
        issue_category="Recalled Toxic Solvent Batch Sold",
        description="Purchased Coldrif syrup for 3-year-old child who developed acute vomiting and lethargy. Pharmacist refused return.",
        adverse_health_event=True,
        patient_age_group="Child (1-12 yrs)",
        consumer_phone="+91 98200 12345",
        status="RESOLVED",
        pipeline_stage=4,
        investigating_officer="Dr. Anand Patil (Drugs Inspector, Zone 3 Mumbai)",
        resolution_notes="Raid conducted jointly with FDA Flying Squad and Local Police. 142 bottles confiscated under formal panchnama. Chemist drug license suspended under Section 22(d). Consumer compensated."
    )
    g2 = models.PGGrievance(
        docket_number="PG-GRIEV-2026-2190",
        batch_number="WD-2049",
        product_name="Woodward's Gripe Water Contaminated Batch",
        sector="BABY_PRODUCTS",
        shop_name="Apollo 24x7 Chemist",
        shop_location="Gokhale Road, Thane West",
        latitude=19.1982,
        longitude=72.9634,
        issue_category="Fungal Spore Contamination in Baby Formulation",
        description="Found visible dark floating sediment inside sealed bottle given to 5-month-old infant. Infant suffered abdominal cramps.",
        adverse_health_event=True,
        patient_age_group="Infant (0-1 yr)",
        consumer_phone="+91 98111 44556",
        status="SEIZURE_DISPATCHED",
        pipeline_stage=3,
        investigating_officer="S. V. Deshmukh (Assistant Commissioner, FDA Thane)",
        resolution_notes="Laboratory culture report confirmed viable Cladosporium fungal mycelia. Seizure notice served to distributor M/s Vardhaman Pharma. Enforcement flying squad deployed."
    )
    g3 = models.PGGrievance(
        docket_number="PG-GRIEV-2026-3341",
        batch_number="CER-892",
        product_name="Nestlé Cerelac Wheat-Apple Baby Cereal",
        sector="BABY_PRODUCTS",
        shop_name="Modern Bazaar Grocery",
        shop_location="M-Block, GK-1, New Delhi",
        latitude=28.5494,
        longitude=77.2346,
        issue_category="Excess Added Sugar in Infant Food",
        description="Package contained batch flagged under FSSAI sugar reformulation order. Store still selling without mandatory warning.",
        adverse_health_event=False,
        patient_age_group="Infant (0-1 yr)",
        consumer_phone="+91 98765 99881",
        status="INVESTIGATING",
        pipeline_stage=2,
        investigating_officer="Meenakshi Sundaram (Food Safety Officer, South Delhi)",
        resolution_notes="Formal statutory sample drawn under Rule 2.4.1 of FSS Rules and forwarded to National Food Laboratory, Ghaziabad."
    )
    g4 = models.PGGrievance(
        docket_number="PG-GRIEV-2026-4812",
        batch_number="AZ-8029",
        product_name="Azicip-500 Spurious Antibiotic Batch",
        sector="HEALTH_PHARMA",
        shop_name="Shree Ram Medicos",
        shop_location="Sector 15, Faridabad",
        latitude=28.4089,
        longitude=77.3178,
        issue_category="Spurious / Fake Medicine with Zero Active Ingredient",
        description="Tablets were powdery, chalky, and dissolved instantaneously in water without bitter taste. Patient fever worsened.",
        adverse_health_event=True,
        patient_age_group="Adult",
        consumer_phone="+91 98990 11223",
        status="REGISTERED",
        pipeline_stage=1,
        investigating_officer="Assigned to Senior Drugs Control Officer (Faridabad Zone)",
        resolution_notes="Docket registered under CDSCO NSQ National Surveillance Tracker. Inspector site visit scheduled within 24 hours."
    )
    g5 = models.PGGrievance(
        docket_number="PG-GRIEV-2026-5501",
        batch_number="LT-1108",
        product_name="Lantus Insulin Glargine",
        sector="HEALTH_PHARMA",
        shop_name="City Lifeline Hospital Pharmacy",
        shop_location="FC Road, Pune",
        latitude=18.5204,
        longitude=73.8567,
        issue_category="Cold-Chain Violation (Warm Insulin Vials)",
        description="Pharmacist dispensed Lantus from an unrefrigerated display carton after 8-hour power cut without generator backup.",
        adverse_health_event=False,
        patient_age_group="Adult",
        consumer_phone="+91 97654 33221",
        status="SEIZURE_DISPATCHED",
        pipeline_stage=3,
        investigating_officer="R. K. Kadam (Drug Inspector, Pune Division)",
        resolution_notes="Temperature logger audit ordered. 18 vials confiscated. Chemist ordered to show cause within 7 days."
    )
    db.add_all([g1, g2, g3, g4, g5])
    db.commit()
    print("ProductGuard AI multi-sector data & grievances seeded successfully with 18 products, 15 inventory items, and 5 pipeline grievances!")

if __name__ == "__main__":
    seed_database()


