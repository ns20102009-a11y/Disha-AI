import random
from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app import models

router = APIRouter(prefix="/api/productguard", tags=["ProductGuard AI"])

# Pydantic Schemas
class GrievanceCreateRequest(BaseModel):
    batch_number: str
    product_name: str
    shop_name: str
    shop_location: str
    sector: Optional[str] = "FOOD_CONSUMABLES" # HEALTH_PHARMA, BABY_PRODUCTS, FOOD_CONSUMABLES
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    issue_category: str
    description: str
    adverse_health_event: Optional[bool] = False
    patient_age_group: Optional[str] = "Adult" # Infant (0-1 yr), Child (1-12 yrs), Adult
    photo_url: Optional[str] = None
    consumer_phone: Optional[str] = None

class OCRSimulateRequest(BaseModel):
    raw_text: Optional[str] = None
    preset_id: Optional[str] = None

@router.get("/test-cases")
def get_test_cases(sector: Optional[str] = None):
    """
    Returns pre-seeded interactive test cases categorized by sector:
    Health & Medicines, Baby Products, and Food & FMCG.
    """
    cases = [
        # --- HEALTH & MEDICINES SECTOR ---
        {
            "id": "test3",
            "sector": "HEALTH_PHARMA",
            "sector_name": "Health & Pharmaceuticals",
            "title": "Coldrif Pediatric Syrup (Toxic DEG Alert)",
            "brand": "Sreshta Pharma",
            "product": "Coldrif Antitussive Pediatric Cough Syrup (100ml)",
            "barcode": "8904032198765",
            "batch_number": "SR-13",
            "expected_verdict": "RECALLED",
            "color": "rose",
            "description": "Carton printed expiry says 2027. BUT batch SR-13 has active CDSCO & Maharashtra FDA Recall for 1.4% Diethylene Glycol (DEG) lethal solvent toxicity."
        },
        {
            "id": "test_azithro_fake",
            "sector": "HEALTH_PHARMA",
            "sector_name": "Health & Pharmaceuticals",
            "title": "Spurious Azicip-500 (0% API Counterfeit Raid)",
            "brand": "Cipla Healthcare (Counterfeit)",
            "product": "Azicip-500 Azithromycin Tablets IP 500mg",
            "barcode": "8901117012011",
            "batch_number": "AZ-8029",
            "expected_verdict": "RECALLED",
            "color": "rose",
            "description": "Spurious drug batch seized in Raigad raid. Laboratory HPLC revealed 0% active antibiotic; contains inert chalk and talc binder. CDSCO NSQ Alert active."
        },
        {
            "id": "test_insulin",
            "sector": "HEALTH_PHARMA",
            "sector_name": "Health & Pharmaceuticals",
            "title": "Lantus Insulin (Cold-Chain Transit Failure)",
            "brand": "Sanofi India",
            "product": "Lantus 100 IU/ml Insulin Glargine Cartridge",
            "barcode": "8901043009941",
            "batch_number": "LT-1108",
            "expected_verdict": "RECALLED",
            "color": "rose",
            "description": "Refrigeration truck compressor failure (>28°C for 42 hours). Denatured insulin protein with loss of biological glycemic potency."
        },
        {
            "id": "test_azithro_safe",
            "sector": "HEALTH_PHARMA",
            "sector_name": "Health & Pharmaceuticals",
            "title": "Azicip-500 Tablets (Genuine & Tested Compliant)",
            "brand": "Cipla Healthcare",
            "product": "Azicip-500 Azithromycin Tablets IP 500mg",
            "barcode": "8901117012011",
            "batch_number": "AZ-8021",
            "expected_verdict": "SAFE",
            "color": "emerald",
            "description": "Passed CDSCO Central Drug Testing Lab. 99.8% assay, dissolution time 5.8m, zero toxic excipients."
        },
        {
            "id": "test_calpol",
            "sector": "HEALTH_PHARMA",
            "sector_name": "Health & Pharmaceuticals",
            "title": "Calpol Paediatric Suspension (Safe & Zero DEG)",
            "brand": "GSK Pharmaceuticals",
            "product": "Calpol Paediatric Oral Suspension 250mg/5ml",
            "barcode": "8901034015522",
            "batch_number": "CAL-991",
            "expected_verdict": "SAFE",
            "color": "emerald",
            "description": "HPLC tested by IPC Ghaziabad. Screened completely free of toxic Diethylene Glycol or Ethylene Glycol solvents."
        },
        {
            "id": "test_monocef",
            "sector": "HEALTH_PHARMA",
            "sector_name": "Health & Pharmaceuticals",
            "title": "Monocef 1g Injection (Expiring in 48 Hours)",
            "brand": "Aristo Pharmaceuticals",
            "product": "Monocef 1g Sterile Ceftriaxone Injection IP",
            "barcode": "8901248003112",
            "batch_number": "MC-4402",
            "expected_verdict": "EXPIRING_SOON",
            "color": "amber",
            "description": "Hospital ICU injectable reaching statutory 48-hour shelf-life limit. Risk of post-reconstitution instability."
        },

        # --- BABY PRODUCTS & INFANT NUTRITION ---
        {
            "id": "test_lactogen",
            "sector": "BABY_PRODUCTS",
            "sector_name": "Baby & Infant Nutrition",
            "title": "Nestlé Lactogen 1 (Zero Cronobacter Formula)",
            "brand": "Nestlé India",
            "product": "Nestlé Lactogen Infant Formula Stage 1 (0-6 Months)",
            "barcode": "8901058852331",
            "batch_number": "LAC-4109",
            "expected_verdict": "SAFE",
            "color": "emerald",
            "description": "Conforms to strict FSSAI Infant Food Regulations. Screened negative for Cronobacter sakazakii and Salmonella. Zero added sucrose."
        },
        {
            "id": "test_cerelac",
            "sector": "BABY_PRODUCTS",
            "sector_name": "Baby & Infant Nutrition",
            "title": "Nestlé Cerelac Wheat-Apple (Excess Sugar Recall)",
            "brand": "Nestlé Nutrition",
            "product": "Nestlé Cerelac Wheat-Apple Baby Cereal with Milk",
            "barcode": "8901058863214",
            "batch_number": "CER-892",
            "expected_verdict": "RECALLED",
            "color": "rose",
            "description": "FSSAI Infant Food Audit flagged 2.7g unpermitted added sugar (sucrose) per serving. Regulatory reformulation & clearance order active."
        },
        {
            "id": "test_gripe_bad",
            "sector": "BABY_PRODUCTS",
            "sector_name": "Baby & Infant Nutrition",
            "title": "Woodward's Gripe Water (Fungal Spore Contamination)",
            "brand": "Woodward's (TTK Healthcare)",
            "product": "Woodward's Gripe Water for Infants (130ml)",
            "barcode": "8901425001221",
            "batch_number": "WD-2049",
            "expected_verdict": "RECALLED",
            "color": "rose",
            "description": "Thane FDA raid detected Cladosporium fungal mycelia and non-permitted synthetic benzoic acid preservative. 14 infant gastrointestinal events logged."
        },
        {
            "id": "test_vitd",
            "sector": "BABY_PRODUCTS",
            "sector_name": "Baby & Infant Nutrition",
            "title": "D-Well Baby Vitamin D3 Drops (Accurate & Safe)",
            "brand": "Sun Pharma Consumer",
            "product": "D-Well Baby Vitamin D3 Pediatric Oral Drops (800 IU/ml)",
            "barcode": "8901117228801",
            "batch_number": "VD-5520",
            "expected_verdict": "SAFE",
            "color": "emerald",
            "description": "Calibrated dropper delivers exact 400 IU per 0.5ml. Tested compliant by CDL Kasauli. Neonatal safe."
        },
        {
            "id": "test_wipes",
            "sector": "BABY_PRODUCTS",
            "sector_name": "Baby & Infant Nutrition",
            "title": "Little's Baby Water Wipes (Expiring in 3 Days)",
            "brand": "Piramal Healthcare",
            "product": "Little's Soft & Gentle Baby Pure Water Wipes",
            "barcode": "8901233008910",
            "batch_number": "LW-712",
            "expected_verdict": "EXPIRING_SOON",
            "color": "amber",
            "description": "Preservative degradation threshold in 72 hours. Risk of bacterial colonization and dryness after unsealing."
        },
        {
            "id": "test_sebamed",
            "sector": "BABY_PRODUCTS",
            "sector_name": "Baby & Infant Nutrition",
            "title": "Sebamed Baby Gentle Wash (pH 5.5 Certified)",
            "brand": "Sebamed Germany / USV",
            "product": "Sebamed Baby Gentle Wash Extra Soft (200ml)",
            "barcode": "4103040114002",
            "batch_number": "SBM-901",
            "expected_verdict": "SAFE",
            "color": "emerald",
            "description": "pH 5.5 clinically verified. Free of parabens, formaldehyde, and phthalates. Ophthalmological tear-free certified."
        },

        # --- FOOD & DAIRY SECTOR ---
        {
            "id": "test1",
            "sector": "FOOD_CONSUMABLES",
            "sector_name": "Food & Dairy Consumables",
            "title": "Amul Taaza Milk (Safe / Verified)",
            "brand": "Amul",
            "product": "Taaza Fresh Toned Milk (1 Litre Tetra)",
            "barcode": "8901262010053",
            "batch_number": "AM-2409",
            "expected_verdict": "SAFE",
            "color": "emerald",
            "description": "Standard retail milk packet. Passed FSSAI microbiology & adulteration tests. Well within expiry date."
        },
        {
            "id": "test2",
            "sector": "FOOD_CONSUMABLES",
            "sector_name": "Food & Dairy Consumables",
            "title": "Harvest Gold Bread (Expiring Tomorrow)",
            "brand": "Harvest Gold",
            "product": "100% Atta Whole Wheat Bread",
            "barcode": "8906012345678",
            "batch_number": "HB-1102",
            "expected_verdict": "EXPIRING_SOON",
            "color": "amber",
            "description": "Fresh bakery loaf. Reaching expiry tomorrow. Dynamic threshold triggers caution & clearance recommendation."
        },
        {
            "id": "test_oil_bad",
            "sector": "FOOD_CONSUMABLES",
            "sector_name": "Food & Dairy Consumables",
            "title": "Fortune Mustard Oil (Argemone Adulteration Recall)",
            "brand": "Fortune",
            "product": "Kachi Ghani Pure Mustard Oil",
            "barcode": "8906007281014",
            "batch_number": "FT-9022",
            "expected_verdict": "RECALLED",
            "color": "rose",
            "description": "Maharashtra FDA raid detected Argemone seed oil contamination and non-permitted synthetic colour in Batch FT-9022."
        }
    ]

    if sector:
        cases = [c for c in cases if c.get("sector") == sector.strip()]
    return cases

@router.get("/verify")
def verify_product_batch(
    batch_number: Optional[str] = None,
    barcode: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Core Batch-Level Intelligence Engine:
    Validates product authenticity, checks specific batch lab reports, computes live countdown,
    and returns a structured safety verdict card across Health, Baby Products, and Food.
    """
    query = db.query(models.PGBatch).join(models.PGProduct)

    if batch_number and barcode:
        query = query.filter(
            models.PGBatch.batch_number.ilike(batch_number.strip()),
            models.PGProduct.barcode == barcode.strip()
        )
    elif batch_number:
        query = query.filter(models.PGBatch.batch_number.ilike(batch_number.strip()))
    elif barcode:
        query = query.filter(models.PGProduct.barcode == barcode.strip())
    else:
        raise HTTPException(status_code=400, detail="Provide at least batch_number or barcode")

    batch = query.first()

    if not batch:
        # Fallback search on Product table only if barcode was provided
        if barcode:
            prod = db.query(models.PGProduct).filter(models.PGProduct.barcode == barcode.strip()).first()
            if prod:
                return {
                    "found": True,
                    "is_known_batch": False,
                    "product": {
                        "id": prod.id,
                        "brand_name": prod.brand_name,
                        "product_name": prod.product_name,
                        "sector": prod.sector,
                        "category": prod.category,
                        "sub_category": prod.sub_category,
                        "fssai_license": prod.fssai_license,
                        "net_quantity": prod.net_quantity,
                        "mrp": prod.mrp,
                        "barcode": prod.barcode
                    },
                    "verdict": "UNKNOWN_BATCH",
                    "verdict_color": "amber",
                    "verdict_title": "🟡 PRODUCT REGISTERED • BATCH UNVERIFIED",
                    "message": f"Brand '{prod.brand_name}' is valid in central registry, but batch '{batch_number or 'N/A'}' has not yet been registered by the distributor."
                }
        raise HTTPException(status_code=404, detail="No matching product or batch found in safety database.")

    product = batch.product
    now = datetime.utcnow()
    total_shelf_seconds = (batch.expiry_date - batch.mfg_date).total_seconds()
    remaining_seconds = (batch.expiry_date - now).total_seconds()
    days_remaining = int(remaining_seconds // 86400)

    # Calculate shelf life percentage remaining
    if total_shelf_seconds > 0:
        shelf_life_percentage = max(0.0, min(100.0, round((remaining_seconds / total_shelf_seconds) * 100, 1)))
    else:
        shelf_life_percentage = 0.0

    # Sector specific advice tone
    is_medicine = product.sector == "HEALTH_PHARMA"
    is_baby = product.sector == "BABY_PRODUCTS"

    # Determine Safety Verdict
    if batch.is_recalled:
        verdict = "CRITICAL_RECALL"
        verdict_color = "red"
        verdict_title = "🔴 CRITICAL ALERT: RECALLED BY REGULATORY AUTHORITY"
        verdict_badge = "DO NOT CONSUME / ADMINISTER"
        countdown_text = "⚠️ RECALLED BATCH — IMMEDIATE SEIZURE NOTICE"
        if is_medicine:
            actionable_advice = (
                f"DO NOT ADMINISTER THIS MEDICINE. CDSCO / State FDA has issued an active recall for Batch {batch.batch_number} "
                f"due to laboratory quality failure ({batch.recall_reason[:90]}...). Return to pharmacy immediately or file a grievance."
            )
        elif is_baby:
            actionable_advice = (
                f"DO NOT FEED THIS PRODUCT TO INFANTS. Batch {batch.batch_number} has been flagged for pediatric health hazard "
                f"({batch.recall_reason[:90]}...). Contact your pediatrician if already consumed and report the store below."
            )
        else:
            actionable_advice = (
                "DO NOT PURCHASE OR INGEST THIS PRODUCT. Regulatory enforcement has flagged this specific batch for laboratory safety failure. "
                "Report this item immediately to the store manager or file a complaint below."
            )
    elif days_remaining < 0:
        verdict = "EXPIRED"
        verdict_color = "red"
        verdict_title = "🔴 EXPIRED PRODUCT — DO NOT USE"
        verdict_badge = "EXPIRED"
        countdown_text = f"🚫 Expired {abs(days_remaining)} days ago"
        actionable_advice = (
            f"This {product.category.lower()} exceeded its statutory shelf life on {batch.expiry_date.strftime('%d-%b-%Y')}. "
            "Sale of expired items violates statutory law. Do not consume."
        )
    elif days_remaining <= 3 or shelf_life_percentage <= 15.0:
        verdict = "EXPIRING_SOON"
        verdict_color = "yellow"
        verdict_title = "🟡 CAUTION: EXPIRING SOON"
        verdict_badge = "EXPIRING SOON"
        countdown_text = f"⏳ {max(days_remaining, 1)} Day{'s' if days_remaining != 1 else ''} Remaining ({shelf_life_percentage}% shelf-life left)"
        actionable_advice = (
            f"Product is approaching statutory expiry ({batch.expiry_date.strftime('%d-%b-%Y')}). "
            "Use promptly. Retailers/chemists should apply clearance markdown or quarantine from active stock."
        )
    else:
        verdict = "SAFE"
        verdict_color = "green"
        verdict_title = "🟢 VERIFIED / SAFE TO USE"
        verdict_badge = "SAFE & COMPLIANT"
        countdown_text = f"⏳ {days_remaining} Days Remaining ({shelf_life_percentage}% shelf-life)"
        actionable_advice = f"Verified genuine and compliant with {batch.regulatory_authority or 'Central Safety Standards'}. Zero active recall orders."

    # Batch vs Product distinction explainer
    if batch.is_recalled:
        distinction = (
            f"Critical Distinction: Brand '{product.brand_name}' holds valid statutory manufacturing license #{product.fssai_license}. "
            f"However, specifically Batch #{batch.batch_number} failed official laboratory safety standards. "
            f"Other batches from this manufacturer may be completely safe."
        )
    else:
        distinction = (
            f"Batch #{batch.batch_number} has been cross-referenced against CDSCO & FSSAI safety registers. "
            f"Tested compliant with prescribed pharmacopoeia / food standards."
        )

    # Traceability Timeline
    timeline = [
        {
            "stage": "Manufacturing & Sterile Batching",
            "date": batch.mfg_date.strftime("%d-%b-%Y"),
            "status": "COMPLETED",
            "details": f"Batch produced at certified facility under Lic #{product.fssai_license}. Storage: {batch.storage_temperature}."
        },
        {
            "stage": "Laboratory Testing & Safety Audit",
            "date": (batch.mfg_date + timedelta(days=2)).strftime("%d-%b-%Y"),
            "status": "FAILED" if batch.is_recalled else "PASSED",
            "details": f"Report: {batch.lab_test_report_id or 'GOVT-LAB-2026'}. {batch.lab_test_summary or 'Standard testing completed.'}"
        },
        {
            "stage": "Distributor & Cold-Chain Supply",
            "date": (batch.mfg_date + timedelta(days=4)).strftime("%d-%b-%Y"),
            "status": "FLAGGED" if batch.is_recalled else "COMPLETED",
            "details": f"Tracked in national inventory registry. Adverse Events: {batch.adverse_events_count}."
        },
        {
            "stage": "Point-of-Sale Verification",
            "date": now.strftime("%d-%b-%Y %H:%M UTC"),
            "status": "ACTIVE",
            "details": "Live authentication via ProductGuard AI neural verification engine."
        }
    ]

    return {
        "found": True,
        "is_known_batch": True,
        "product": {
            "id": product.id,
            "brand_name": product.brand_name,
            "product_name": product.product_name,
            "sector": product.sector,
            "category": product.category,
            "sub_category": product.sub_category,
            "fssai_license": product.fssai_license,
            "net_quantity": product.net_quantity,
            "mrp": product.mrp,
            "barcode": product.barcode,
            "image_url": product.image_url
        },
        "batch": {
            "id": batch.id,
            "batch_number": batch.batch_number,
            "mfg_date": batch.mfg_date.strftime("%d-%b-%Y"),
            "expiry_date": batch.expiry_date.strftime("%d-%b-%Y"),
            "status": batch.status,
            "is_recalled": batch.is_recalled,
            "recall_reason": batch.recall_reason,
            "regulatory_authority": batch.regulatory_authority,
            "lab_test_report_id": batch.lab_test_report_id,
            "lab_test_summary": batch.lab_test_summary,
            "hazard_level": batch.hazard_level,
            "storage_temperature": batch.storage_temperature,
            "adverse_events_count": batch.adverse_events_count
        },
        "intelligence": {
            "verdict": verdict,
            "verdict_color": verdict_color,
            "verdict_title": verdict_title,
            "verdict_badge": verdict_badge,
            "days_remaining": days_remaining,
            "shelf_life_percentage": shelf_life_percentage,
            "countdown_text": countdown_text,
            "actionable_advice": actionable_advice,
            "batch_vs_product_distinction": distinction,
            "verification_source": batch.regulatory_authority,
            "audit_timestamp": now.strftime("%Y-%m-%d %H:%M:%S UTC"),
            "timeline": timeline
        }
    }

@router.post("/simulate-ocr")
def simulate_ocr_scan(payload: OCRSimulateRequest, db: Session = Depends(get_db)):
    """
    Simulates intelligent multi-modal OCR packaging reader supporting all sector test presets.
    """
    preset_map = {
        "test1": ("AM-2409", "8901262010053"), # Amul Milk Safe
        "test2": ("HB-1102", "8906012345678"), # Harvest Bread Expiring
        "test3": ("SR-13", "8904032198765"),   # Coldrif Syrup Recalled
        "test_azithro_safe": ("AZ-8021", "8901117012011"), # Azithro Safe
        "test_azithro_fake": ("AZ-8029", "8901117012011"), # Spurious Azithro
        "test_insulin": ("LT-1108", "8901043009941"),      # Lantus Cold-Chain failure
        "test_calpol": ("CAL-991", "8901034015522"),       # Calpol Safe
        "test_monocef": ("MC-4402", "8901248003112"),      # Monocef Expiring
        "test_lactogen": ("LAC-4109", "8901058852331"),    # Lactogen Safe
        "test_cerelac": ("CER-892", "8901058863214"),      # Cerelac High Sugar
        "test_gripe_bad": ("WD-2049", "8901425001221"),    # Gripe Fungal
        "test_gripe_safe": ("WD-2041", "8901425001221"),   # Gripe Safe
        "test_vitd": ("VD-5520", "8901117228801"),         # Baby Vit D3 Safe
        "test_wipes": ("LW-712", "8901233008910"),         # Baby Wipes Expiring
        "test_sebamed": ("SBM-901", "4103040114002"),      # Sebamed Safe
        "test_oil_bad": ("FT-9022", "8906007281014"),      # Mustard Oil Recall
    }

    if payload.preset_id and payload.preset_id in preset_map:
        batch_no, barcode = preset_map[payload.preset_id]
        return verify_product_batch(batch_number=batch_no, barcode=barcode, db=db)

    # Custom OCR parsing simulation
    raw = (payload.raw_text or "").upper()
    for p_id, (b_no, bar) in preset_map.items():
        if b_no in raw:
            return verify_product_batch(batch_number=b_no, barcode=bar, db=db)

    # Default fallback to Amul Taaza
    return verify_product_batch(batch_number="AM-2409", db=db)

@router.get("/sector-data")
def get_sector_data(sector: str, db: Session = Depends(get_db)):
    """
    Returns dedicated sector dashboard metrics, products, active alerts, and regulatory guidelines.
    """
    sec = sector.strip().upper()
    products = db.query(models.PGProduct).filter(models.PGProduct.sector == sec).all()
    
    total_products = len(products)
    total_batches = 0
    safe_batches = 0
    recalled_batches = 0
    expiring_batches = 0
    product_list = []

    for p in products:
        for b in p.batches:
            total_batches += 1
            if b.is_recalled:
                recalled_batches += 1
            elif b.status == "SAFE":
                safe_batches += 1
            elif b.status == "EXPIRING_SOON":
                expiring_batches += 1

        product_list.append({
            "id": p.id,
            "brand_name": p.brand_name,
            "product_name": p.product_name,
            "category": p.category,
            "sub_category": p.sub_category,
            "fssai_license": p.fssai_license,
            "net_quantity": p.net_quantity,
            "mrp": p.mrp,
            "barcode": p.barcode,
            "batch_count": len(p.batches),
            "batches": [
                {
                    "batch_number": b.batch_number,
                    "status": b.status,
                    "is_recalled": b.is_recalled,
                    "hazard_level": b.hazard_level,
                    "expiry_date": b.expiry_date.strftime("%d-%b-%Y"),
                    "storage_temperature": b.storage_temperature,
                    "adverse_events": b.adverse_events_count,
                    "recall_reason": b.recall_reason
                } for b in p.batches
            ]
        })

    grievances_count = db.query(models.PGGrievance).filter(models.PGGrievance.sector == sec).count()

    return {
        "sector": sec,
        "total_products": total_products,
        "total_batches": total_batches,
        "safe_batches": safe_batches,
        "recalled_batches": recalled_batches,
        "expiring_batches": expiring_batches,
        "grievances_count": grievances_count,
        "products": product_list
    }

@router.get("/cdsco-alerts")
def get_cdsco_alerts():
    """
    Returns active Central Drugs Standard Control Organisation (CDSCO) & State Drug Control alerts.
    """
    return [
        {
            "alert_id": "CDSCO-DEG-2026-89",
            "date": "August 2026",
            "product": "Coldrif Antitussive Pediatric Cough Syrup",
            "batch": "SR-13",
            "hazard": "CRITICAL / LETHAL",
            "violation": "1.4% Diethylene Glycol (DEG) industrial solvent impurity detected above fatal pediatric limit.",
            "enforcement": "Nationwide seizure order under Section 26 Drugs & Cosmetics Act. Chemist drug license suspended."
        },
        {
            "alert_id": "CDSCO-NSQ-2026-118",
            "date": "July 2026",
            "product": "Azicip-500 Azithromycin Tablets (Counterfeit)",
            "batch": "AZ-8029",
            "hazard": "HIGH / SPURIOUS DRUG",
            "violation": "0% Active Pharmaceutical Ingredient (API). Tablet composed of inert calcium carbonate and talc.",
            "enforcement": "Raigad illegal manufacturing unit sealed. 12,000 strips confiscated. FIR registered under Sec 27(c)."
        },
        {
            "alert_id": "MH-FDA-COLD-2026-72",
            "date": "June 2026",
            "product": "Lantus 100 IU/ml Insulin Glargine",
            "batch": "LT-1108",
            "hazard": "CRITICAL / THERMAL FAILURE",
            "violation": "Cold-chain temperature excursion above 28°C for 42 hours during highway transit, denaturing insulin protein.",
            "enforcement": "Stock quarantined across 4 hospital chains in Pune and Mumbai. Biological destruction ordered."
        }
    ]

@router.get("/infant-safety-alerts")
def get_infant_safety_alerts():
    """
    Returns active FSSAI & Paediatric Health Directorate Infant Food Audits.
    """
    return [
        {
            "alert_id": "FSSAI-INF-2026-899",
            "date": "August 2026",
            "product": "Nestlé Cerelac Wheat-Apple Baby Cereal (6+ Months)",
            "batch": "CER-892",
            "hazard": "HIGH / NUTRITIONAL VIOLATION",
            "violation": "2.7g added sucrose/maltodextrin per serving detected in infant cereal, violating FSSAI Infant Nutrition Standards 2026.",
            "enforcement": "Reformulation order served to manufacturer. Batches recalled from retail distribution."
        },
        {
            "alert_id": "MH-FDA-INF-2026-302",
            "date": "July 2026",
            "product": "Woodward's Gripe Water for Infants",
            "batch": "WD-2049",
            "hazard": "CRITICAL / FUNGAL CONTAMINATION",
            "violation": "Cladosporium fungal mycelia and non-permitted synthetic benzoic acid preservative detected in baby formulation.",
            "enforcement": "Confiscated by Thane FDA Flying Squad following 14 infant gastrointestinal complaints."
        },
        {
            "alert_id": "FSSAI-CRONO-2026-44",
            "date": "June 2026",
            "product": "National Infant Formula Surveillance Directive",
            "batch": "All Stage 1 Brands",
            "hazard": "MANDATORY SCREENING",
            "violation": "Mandatory Cronobacter sakazakii & Salmonella zero-tolerance microbiological testing reinforced for all powdered infant formulas.",
            "enforcement": "100% batch release certification made mandatory before retail inwarding."
        }
    ]

@router.post("/grievance")
def report_grievance(req: GrievanceCreateRequest, db: Session = Depends(get_db)):
    """
    Generates official consumer grievance docket with sector classification and 4-stage tracking.
    """
    docket_no = f"PG-GRIEV-2026-{random.randint(1000, 9999)}"
    
    # Auto assign investigating officer based on sector
    if req.sector == "HEALTH_PHARMA":
        officer = "Assigned to District Drug Inspector & State CDSCO Directorate"
    elif req.sector == "BABY_PRODUCTS":
        officer = "Assigned to Special Paediatric Food Safety Squad & FSSAI Directorate"
    else:
        officer = "Assigned to District Food Safety Officer"

    grievance = models.PGGrievance(
        docket_number=docket_no,
        batch_number=req.batch_number,
        product_name=req.product_name,
        sector=req.sector or "FOOD_CONSUMABLES",
        shop_name=req.shop_name,
        shop_location=req.shop_location,
        latitude=req.latitude or 19.0760,
        longitude=req.longitude or 72.8777,
        issue_category=req.issue_category,
        description=req.description,
        adverse_health_event=req.adverse_health_event or False,
        patient_age_group=req.patient_age_group or "Adult",
        photo_url=req.photo_url or "/static/uploads/sample_evidence.jpg",
        consumer_phone=req.consumer_phone or "+91 98000 00000",
        status="INVESTIGATING" if req.adverse_health_event else "REGISTERED",
        pipeline_stage=2 if req.adverse_health_event else 1,
        investigating_officer=officer,
        resolution_notes="Statutory grievance logged. Official docket generated for regulatory verification."
    )
    db.add(grievance)
    db.commit()
    db.refresh(grievance)

    return {
        "status": "success",
        "docket_number": docket_no,
        "message": f"Official {req.sector} grievance registered and dispatched to Regulatory Flying Squad.",
        "docket": {
            "id": grievance.id,
            "docket_number": grievance.docket_number,
            "sector": grievance.sector,
            "batch_number": grievance.batch_number,
            "product_name": grievance.product_name,
            "shop_name": grievance.shop_name,
            "issue_category": grievance.issue_category,
            "adverse_health_event": grievance.adverse_health_event,
            "patient_age_group": grievance.patient_age_group,
            "status": grievance.status,
            "pipeline_stage": grievance.pipeline_stage,
            "investigating_officer": grievance.investigating_officer,
            "created_at": grievance.created_at.strftime("%Y-%m-%d %H:%M:%S UTC")
        }
    }

@router.get("/grievances/track/{docket_number}")
def track_grievance(docket_number: str, db: Session = Depends(get_db)):
    """
    Live Grievance Tracker: Returns the 4-stage enforcement pipeline and live case status.
    """
    g = db.query(models.PGGrievance).filter(models.PGGrievance.docket_number.ilike(docket_number.strip())).first()
    if not g:
        raise HTTPException(status_code=404, detail="Grievance docket not found.")

    pipeline = [
        {
            "stage_num": 1,
            "title": "Docket Registered & Formally Logged",
            "status": "COMPLETED",
            "time": g.created_at.strftime("%d-%b-%Y %H:%M"),
            "desc": f"Consumer grievance docket #{g.docket_number} logged in National Portal."
        },
        {
            "stage_num": 2,
            "title": "Assigned to Regulatory Enforcement Officer",
            "status": "COMPLETED" if g.pipeline_stage >= 2 else "PENDING",
            "time": (g.created_at + timedelta(hours=2)).strftime("%d-%b-%Y %H:%M") if g.pipeline_stage >= 2 else "In Progress",
            "desc": f"Assigned to: {g.investigating_officer or 'Regulatory Officer'}. Sample verification initiated."
        },
        {
            "stage_num": 3,
            "title": "Field Inspection & Legal Seizure Notice",
            "status": "COMPLETED" if g.pipeline_stage >= 3 else ("IN_PROGRESS" if g.pipeline_stage == 2 else "PENDING"),
            "time": (g.created_at + timedelta(hours=14)).strftime("%d-%b-%Y %H:%M") if g.pipeline_stage >= 3 else "Pending inspection",
            "desc": "On-site chemist/store inspection. Panchnama issued under Food & Drugs Act."
        },
        {
            "stage_num": 4,
            "title": "Final Resolution & Stock Quarantine",
            "status": "COMPLETED" if g.pipeline_stage >= 4 else "PENDING",
            "time": (g.created_at + timedelta(hours=36)).strftime("%d-%b-%Y %H:%M") if g.pipeline_stage >= 4 else "Awaiting report",
            "desc": g.resolution_notes or "Awaiting final laboratory confirmation."
        }
    ]

    return {
        "found": True,
        "docket": {
            "docket_number": g.docket_number,
            "sector": g.sector,
            "product_name": g.product_name,
            "batch_number": g.batch_number,
            "shop_name": g.shop_name,
            "shop_location": g.shop_location,
            "issue_category": g.issue_category,
            "adverse_health_event": g.adverse_health_event,
            "patient_age_group": g.patient_age_group,
            "status": g.status,
            "pipeline_stage": g.pipeline_stage,
            "investigating_officer": g.investigating_officer,
            "resolution_notes": g.resolution_notes,
            "created_at": g.created_at.strftime("%Y-%m-%d %H:%M:%S UTC")
        },
        "pipeline": pipeline
    }

@router.get("/grievances")
def list_grievances(sector: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(models.PGGrievance)
    if sector:
        query = query.filter(models.PGGrievance.sector == sector.strip().upper())
    items = query.order_by(models.PGGrievance.id.desc()).all()
    return items

@router.get("/inventory")
def get_retailer_inventory(sector: Optional[str] = None, db: Session = Depends(get_db)):
    """
    Retailer Mode: Returns real-time shelf inventory with health indicators across pharmacies & stores.
    """
    query = db.query(models.PGInventory).join(models.PGBatch).join(models.PGProduct)
    if sector:
        query = query.filter(models.PGProduct.sector == sector.strip().upper())
    
    items = query.all()
    results = []
    now = datetime.utcnow()

    for item in items:
        batch = item.batch
        product = batch.product
        days_left = (batch.expiry_date - now).days

        # Health status
        if batch.is_recalled:
            health = "RECALLED"
            health_color = "red"
        elif days_left < 0:
            health = "EXPIRED"
            health_color = "red"
        elif days_left <= 3:
            health = "EXPIRING_SOON"
            health_color = "yellow"
        else:
            health = "SAFE"
            health_color = "green"

        results.append({
            "id": item.id,
            "store_name": item.store_name,
            "store_location": item.store_location,
            "stock_quantity": item.stock_quantity,
            "marked_for_removal": item.marked_for_removal,
            "sector": product.sector,
            "brand_name": product.brand_name,
            "product_name": product.product_name,
            "category": product.category,
            "sub_category": product.sub_category,
            "barcode": product.barcode,
            "batch_number": batch.batch_number,
            "mfg_date": batch.mfg_date.strftime("%d-%b-%Y"),
            "expiry_date": batch.expiry_date.strftime("%d-%b-%Y"),
            "storage_temperature": batch.storage_temperature,
            "days_left": days_left,
            "health_status": health,
            "health_color": health_color,
            "is_recalled": batch.is_recalled,
            "recall_reason": batch.recall_reason,
            "last_scanned": item.last_scanned_at.strftime("%d-%b-%Y %H:%M")
        })

    return results

@router.post("/inventory/{item_id}/toggle-removal")
def toggle_inventory_removal(item_id: int, db: Session = Depends(get_db)):
    """
    Retailer action: One-tap 'Mark for Removal / Return to Distributor'.
    """
    item = db.query(models.PGInventory).filter(models.PGInventory.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Inventory item not found")

    item.marked_for_removal = not item.marked_for_removal
    db.commit()

    return {
        "status": "success",
        "item_id": item.id,
        "marked_for_removal": item.marked_for_removal,
        "message": "Stock marked for immediate quarantine & distributor return." if item.marked_for_removal else "Stock returned to active shelf status."
    }

@router.get("/fda-alerts")
def get_fda_alerts():
    """
    Returns active regulatory alerts and Maharashtra FDA / IAS Tukaram Mundhe campaign findings.
    """
    return {
        "case_study": {
            "authority": "Maharashtra Food & Drug Administration (FDA)",
            "commissioner": "IAS Tukaram Mundhe Special Enforcement Campaign",
            "total_raids_conducted": "3,000+",
            "samples_collected": "37,604",
            "samples_tested": "32,604",
            "failed_samples": "15,268 (46.8%)",
            "primary_violations": [
                "Toxic chemical contaminants (Diethylene Glycol in pediatric syrups)",
                "Falsified / Spurious antibiotics with 0% active ingredient",
                "Excess hidden added sucrose in infant complementary weaning foods",
                "Fungal contamination in infant gripe water digestive solutions",
                "Cold-chain transit failure in biologicals & insulin"
            ],
            "the_latency_gap": "Official lab reports take weeks to publish in gazettes, leaving consumers unaware at retail counters."
        }
    }

@router.get("/stats")
def get_productguard_stats(db: Session = Depends(get_db)):
    total_products = db.query(models.PGProduct).count()
    total_batches = db.query(models.PGBatch).count()
    safe_batches = db.query(models.PGBatch).filter(models.PGBatch.status == "SAFE").count()
    recalled_batches = db.query(models.PGBatch).filter(models.PGBatch.is_recalled == True).count()
    expiring_batches = db.query(models.PGBatch).filter(models.PGBatch.status == "EXPIRING_SOON").count()
    total_grievances = db.query(models.PGGrievance).count()

    # Sector specific breakdown
    health_products = db.query(models.PGProduct).filter(models.PGProduct.sector == "HEALTH_PHARMA").count()
    health_recalls = db.query(models.PGBatch).join(models.PGProduct).filter(
        models.PGProduct.sector == "HEALTH_PHARMA",
        models.PGBatch.is_recalled == True
    ).count()

    baby_products = db.query(models.PGProduct).filter(models.PGProduct.sector == "BABY_PRODUCTS").count()
    baby_recalls = db.query(models.PGBatch).join(models.PGProduct).filter(
        models.PGProduct.sector == "BABY_PRODUCTS",
        models.PGBatch.is_recalled == True
    ).count()

    return {
        "total_products": total_products,
        "total_batches": total_batches,
        "safe_batches": safe_batches,
        "recalled_batches": recalled_batches,
        "expiring_batches": expiring_batches,
        "total_grievances": total_grievances,
        "sectors": {
            "health_pharma": {
                "products": health_products,
                "recalls": health_recalls
            },
            "baby_products": {
                "products": baby_products,
                "recalls": baby_recalls
            }
        }
    }
