/**
 * DISHA AI Bilingual Translation Dictionary (English / Hindi)
 * National Legal Metrology Portal - Government of India
 */

const translations = {
    en: {
        system_title: "DISHA AI",
        system_subtitle: "Legal Metrology Online Verification Portal",
        nav_home: "Home",
        nav_trader: "Trader Portal",
        nav_inspector: "Inspector (LMO)",
        nav_admin: "Ministry Admin",
        nav_api: "API Docs",
        nav_scan: "Scan Scale QR",
        hero_tag: "National Legal Metrology Portal • Government of India",
        hero_title: "Online Verification & Digital Stamping System for Weighing Instruments",
        hero_desc: "Replacing physical lead stamping and easily-forged paper certificates with GPS-geofenced field verifications, tamper-proof cryptographic QR seals, and instant public citizen verification.",
        btn_trader: "Enter Trader Portal",
        btn_inspector: "Inspector (LMO) App",
        btn_demo: "Explore Live Verification Showcase",
        role_heading: "Choose Your Operational Role",
        role_sub: "Explore how each stakeholder interacts with the DISHA AI ecosystem",
        trader_role_title: "1. Trader / Scale Owner",
        trader_role_desc: "Register new commercial scales, platform balances or weighbridges. Calculate statutory verification fees and download official QR seal stickers.",
        inspector_role_title: "2. Field Officer (LMO)",
        inspector_role_desc: "Geofenced field inspections. App blocks fake approvals unless within 150m of the shop. Run OIML R-76 tests and read live IoT scale weights directly.",
        citizen_role_title: "3. Citizen & Consumer",
        citizen_role_desc: "Scan the QR sticker on any shop scale to verify genuine government calibration. View validity dates and report short-weighing fraud in 1 click.",
        admin_role_title: "4. Ministry Admin",
        admin_role_desc: "National dashboard tracking compliance rates, overdue re-verifications, inspector audit trails, and consumer grievance heatmaps."
    },
    hi: {
        system_title: "DISHA AI",
        system_subtitle: "विधिक मापविज्ञान ऑनलाइन सत्यापन एवं मुद्रण पोर्टल",
        nav_home: "मुख्य पृष्ठ",
        nav_trader: "व्यापारी पोर्टल",
        nav_inspector: "निरीक्षक (LMO)",
        nav_admin: "मंत्रालय डैशबोर्ड",
        nav_api: "API प्रलेखन",
        nav_scan: "QR कोड स्कैन करें",
        hero_tag: "राष्ट्रीय विधिक मापविज्ञान पोर्टल • भारत सरकार",
        hero_title: "वजन और माप उपकरणों के लिए ऑनलाइन सत्यापन एवं डिजिटल मुद्रांकन प्रणाली",
        hero_desc: "कागजी प्रमाणपत्रों और नकली सील की जगह GPS-जियोफेंसिंग, छेड़छाड़-रहित डिजिटल QR सील और त्वरित उपभोक्ता सत्यापन प्रणाली।",
        btn_trader: "व्यापारी पोर्टल खोलें",
        btn_inspector: "निरीक्षक (LMO) ऐप",
        btn_demo: "लाइव सत्यापन प्रदर्शनी देखें",
        role_heading: "अपनी परिचालन भूमिका चुनें",
        role_sub: "जानिए कैसे विभिन्न हितधारक DISHA AI प्रणाली से जुड़ते हैं",
        trader_role_title: "१. व्यापारी / उपकरण स्वामी",
        trader_role_desc: "नए तौल उपकरणों व धर्मकांटों का पंजीकरण करें, विधिक सत्यापन शुल्क जमा करें और आधिकारिक डिजिटल QR स्टिकर प्राप्त करें।",
        inspector_role_title: "२. विधिक मापविज्ञान अधिकारी (LMO)",
        inspector_role_desc: "जियोफेंस्ड ऑन-साइट निरीक्षण। दुकान से 150 मीटर दूर होने पर सत्यापन स्वतः अवरुद्ध। OIML R-76 परीक्षण व IoT लाइव तौल जांच।",
        citizen_role_title: "३. नागरिक एवं उपभोक्ता",
        citizen_role_desc: "दुकान के तराजू पर लगे QR कोड को स्कैन करके सरकारी सत्यापन की पुष्टि करें और घटतौली की तुरंत शिकायत दर्ज करें।",
        admin_role_title: "४. मंत्रालय प्रशासन",
        admin_role_desc: "राष्ट्रीय अनुपालन दर, नवीनीकरण अलर्ट, अधिकारियों का ऑडिट ट्रेल और उपभोक्ता शिकायतों की निगरानी।"
    }
};

function getLanguage() {
    return localStorage.getItem('disha_ai_lang') || localStorage.getItem('emapan_lang') || 'en';
}

function setLanguage(lang) {
    localStorage.setItem('disha_ai_lang', lang);
    applyTranslations();
}

function applyTranslations() {
    const lang = getLanguage();
    const dict = translations[lang] || translations.en;

    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (dict[key]) {
            el.textContent = dict[key];
        }
    });

    const toggleBtn = document.getElementById('lang-toggle-btn');
    if (toggleBtn) {
        toggleBtn.textContent = lang === 'en' ? 'हिन्दी' : 'English';
    }
}

document.addEventListener('DOMContentLoaded', () => {
    applyTranslations();
});
