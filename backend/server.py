from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict
import uuid
from datetime import datetime, timezone
import random

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Define Models
class DistrictPerformance(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    state_code: str
    state_name: str
    district_code: str
    district_name: str
    month: int
    year: int
    
    # Key metrics
    total_job_cards: int
    active_job_cards: int
    total_workers: int
    active_workers: int
    person_days_generated: int
    average_days_per_household: float
    women_person_days: int
    sc_person_days: int
    st_person_days: int
    
    # Financial
    total_budget_allocated: float
    total_expenditure: float
    wage_expenditure: float
    material_expenditure: float
    average_wage_per_day: float
    
    # Works
    total_works: int
    completed_works: int
    ongoing_works: int
    
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class State(BaseModel):
    model_config = ConfigDict(extra="ignore")
    state_code: str
    state_name: str
    state_name_hi: str  # Hindi name


class District(BaseModel):
    model_config = ConfigDict(extra="ignore")
    district_code: str
    district_name: str
    district_name_hi: str  # Hindi name
    state_code: str
    state_name: str


class TranslationResponse(BaseModel):
    key: str
    translations: Dict[str, str]


# Translations for UI
TRANSLATIONS = {
    "app_title": {
        "en": "MGNREGA District Dashboard",
        "hi": "मनरेगा जिला डैशबोर्ड",
        "ta": "MGNREGA மாவட்ட டாஷ்போர்டு",
        "te": "MGNREGA జిల్లా డాష్‌బోర్డ్",
        "bn": "MGNREGA জেলা ড্যাশবোর্ড"
    },
    "select_state": {
        "en": "Select Your State",
        "hi": "अपना राज्य चुनें",
        "ta": "உங்கள் மாநிலத்தைத் தேர்ந்தெடுக்கவும்",
        "te": "మీ రాష్ట్రాన్ని ఎంచుకోండి",
        "bn": "আপনার রাজ্য নির্বাচন করুন"
    },
    "select_district": {
        "en": "Select Your District",
        "hi": "अपना जिला चुनें",
        "ta": "உங்கள் மாவட்டத்தைத் தேர்ந்தெடுக்கவும்",
        "te": "మీ జిల్లాను ఎంచుకోండి",
        "bn": "আপনার জেলা নির্বাচন করুন"
    },
    "performance_summary": {
        "en": "Performance Summary",
        "hi": "प्रदर्शन सारांश",
        "ta": "செயல்திறன் சுருக்கம்",
        "te": "పనితీరు సారాంశం",
        "bn": "কর্মক্ষমতা সারসংক্ষেপ"
    },
    "active_workers": {
        "en": "Active Workers",
        "hi": "सक्रिय कामगार",
        "ta": "செயலில் உள்ள தொழிலாளர்கள்",
        "te": "క్రియాశీల కార్మికులు",
        "bn": "সক্রিয় শ্রমিক"
    },
    "person_days": {
        "en": "Person Days Generated",
        "hi": "व्यक्ति-दिवस उत्पन्न",
        "ta": "நபர் நாட்கள் உருவாக்கப்பட்டது",
        "te": "వ్యక్తి రోజులు సృష్టించబడ్డాయి",
        "bn": "ব্যক্তি দিন তৈরি"
    },
    "budget_utilization": {
        "en": "Budget Used",
        "hi": "बजट उपयोग",
        "ta": "பட்ஜெட் பயன்படுத்தப்பட்டது",
        "te": "బడ్జెట్ ఉపయోగించబడింది",
        "bn": "বাজেট ব্যবহৃত"
    },
    "works_completed": {
        "en": "Works Completed",
        "hi": "पूर्ण कार्य",
        "ta": "முடிக்கப்பட்ட வேலைகள்",
        "te": "పూర్తయిన పనులు",
        "bn": "সম্পন্ন কাজ"
    },
    "avg_wage": {
        "en": "Average Daily Wage",
        "hi": "औसत दैनिक मजदूरी",
        "ta": "சராசரி தினசரி ஊதியம்",
        "te": "సగటు రోజువారీ వేతనం",
        "bn": "গড় দৈনিক মজুরি"
    },
    "women_participation": {
        "en": "Women's Participation",
        "hi": "महिला भागीदारी",
        "ta": "பெண்கள் பங்கேற்பு",
        "te": "మహిళల భాగస్వామ్యం",
        "bn": "মহিলা অংশগ্রহণ"
    },
    "view_details": {
        "en": "View Details",
        "hi": "विवरण देखें",
        "ta": "விவரங்களைப் பார்க்கவும்",
        "te": "వివరాలను చూడండి",
        "bn": "বিস্তারিত দেখুন"
    },
    "no_data": {
        "en": "No data available for this period",
        "hi": "इस अवधि के लिए कोई डेटा उपलब्ध नहीं है",
        "ta": "இந்த காலத்திற்கு தரவு கிடைக்கவில்லை",
        "te": "ఈ కాలానికి డేటా అందుబాటులో లేదు",
        "bn": "এই সময়ের জন্য কোন ডেটা উপলব্ধ নেই"
    }
}


# Routes
@api_router.get("/")
async def root():
    return {"message": "MGNREGA District Performance API", "version": "1.0"}


@api_router.get("/states", response_model=List[State])
async def get_states():
    """Get all states"""
    states = await db.states.find({}, {"_id": 0}).to_list(100)
    if not states:
        # Initialize with sample data
        await initialize_sample_data()
        states = await db.states.find({}, {"_id": 0}).to_list(100)
    return states


@api_router.get("/districts/{state_code}", response_model=List[District])
async def get_districts(state_code: str):
    """Get all districts for a state"""
    districts = await db.districts.find({"state_code": state_code}, {"_id": 0}).to_list(100)
    if not districts:
        raise HTTPException(status_code=404, detail="No districts found for this state")
    return districts


@api_router.get("/performance/{district_code}", response_model=List[DistrictPerformance])
async def get_district_performance(district_code: str, limit: int = 12):
    """Get performance data for a district (last N months)"""
    performances = await db.performances.find(
        {"district_code": district_code},
        {"_id": 0}
    ).sort("year", -1).sort("month", -1).limit(limit).to_list(limit)
    
    # Convert ISO string timestamps back to datetime
    for perf in performances:
        if isinstance(perf.get('updated_at'), str):
            perf['updated_at'] = datetime.fromisoformat(perf['updated_at'])
    
    if not performances:
        raise HTTPException(status_code=404, detail="No performance data found")
    return performances


@api_router.get("/translations", response_model=List[TranslationResponse])
async def get_translations():
    """Get all translations"""
    return [TranslationResponse(key=k, translations=v) for k, v in TRANSLATIONS.items()]


@api_router.get("/translations/{language}")
async def get_language_translations(language: str):
    """Get translations for a specific language"""
    result = {}
    for key, translations in TRANSLATIONS.items():
        result[key] = translations.get(language, translations["en"])
    return result


async def initialize_sample_data():
    """Initialize database with sample data"""
    
    # All major states
    states = [
        {"state_code": "AP", "state_name": "Andhra Pradesh", "state_name_hi": "आंध्र प्रदेश"},
        {"state_code": "AR", "state_name": "Arunachal Pradesh", "state_name_hi": "अरुणाचल प्रदेश"},
        {"state_code": "AS", "state_name": "Assam", "state_name_hi": "असम"},
        {"state_code": "BR", "state_name": "Bihar", "state_name_hi": "बिहार"},
        {"state_code": "CT", "state_name": "Chhattisgarh", "state_name_hi": "छत्तीसगढ़"},
        {"state_code": "GA", "state_name": "Goa", "state_name_hi": "गोवा"},
        {"state_code": "GJ", "state_name": "Gujarat", "state_name_hi": "गुजरात"},
        {"state_code": "HR", "state_name": "Haryana", "state_name_hi": "हरियाणा"},
        {"state_code": "HP", "state_name": "Himachal Pradesh", "state_name_hi": "हिमाचल प्रदेश"},
        {"state_code": "JH", "state_name": "Jharkhand", "state_name_hi": "झारखंड"},
        {"state_code": "KA", "state_name": "Karnataka", "state_name_hi": "कर्नाटक"},
        {"state_code": "KL", "state_name": "Kerala", "state_name_hi": "केरल"},
        {"state_code": "MP", "state_name": "Madhya Pradesh", "state_name_hi": "मध्य प्रदेश"},
        {"state_code": "MH", "state_name": "Maharashtra", "state_name_hi": "महाराष्ट्र"},
        {"state_code": "MN", "state_name": "Manipur", "state_name_hi": "मणिपुर"},
        {"state_code": "ML", "state_name": "Meghalaya", "state_name_hi": "मेघालय"},
        {"state_code": "MZ", "state_name": "Mizoram", "state_name_hi": "मिजोरम"},
        {"state_code": "NL", "state_name": "Nagaland", "state_name_hi": "नागालैंड"},
        {"state_code": "OR", "state_name": "Odisha", "state_name_hi": "ओडिशा"},
        {"state_code": "PB", "state_name": "Punjab", "state_name_hi": "पंजाब"},
        {"state_code": "RJ", "state_name": "Rajasthan", "state_name_hi": "राजस्थान"},
        {"state_code": "SK", "state_name": "Sikkim", "state_name_hi": "सिक्किम"},
        {"state_code": "TN", "state_name": "Tamil Nadu", "state_name_hi": "तमिलनाडु"},
        {"state_code": "TG", "state_name": "Telangana", "state_name_hi": "तेलंगाना"},
        {"state_code": "TR", "state_name": "Tripura", "state_name_hi": "त्रिपुरा"},
        {"state_code": "UP", "state_name": "Uttar Pradesh", "state_name_hi": "उत्तर प्रदेश"},
        {"state_code": "UT", "state_name": "Uttarakhand", "state_name_hi": "उत्तराखंड"},
        {"state_code": "WB", "state_name": "West Bengal", "state_name_hi": "पश्चिम बंगाल"},
    ]
    
    # Comprehensive districts for all states
    districts = [
        # Andhra Pradesh
        {"district_code": "AP001", "district_name": "Visakhapatnam", "district_name_hi": "विशाखापत्तनम", "state_code": "AP", "state_name": "Andhra Pradesh"},
        {"district_code": "AP002", "district_name": "Vijayawada", "district_name_hi": "विजयवाड़ा", "state_code": "AP", "state_name": "Andhra Pradesh"},
        {"district_code": "AP003", "district_name": "Guntur", "district_name_hi": "गुंटूर", "state_code": "AP", "state_name": "Andhra Pradesh"},
        {"district_code": "AP004", "district_name": "Nellore", "district_name_hi": "नेल्लोर", "state_code": "AP", "state_name": "Andhra Pradesh"},
        {"district_code": "AP005", "district_name": "Kurnool", "district_name_hi": "कुरनूल", "state_code": "AP", "state_name": "Andhra Pradesh"},
        
        # Arunachal Pradesh
        {"district_code": "AR001", "district_name": "Itanagar", "district_name_hi": "ईटानगर", "state_code": "AR", "state_name": "Arunachal Pradesh"},
        {"district_code": "AR002", "district_name": "Tawang", "district_name_hi": "तवांग", "state_code": "AR", "state_name": "Arunachal Pradesh"},
        {"district_code": "AR003", "district_name": "Changlang", "district_name_hi": "चांगलांग", "state_code": "AR", "state_name": "Arunachal Pradesh"},
        
        # Assam
        {"district_code": "AS001", "district_name": "Guwahati", "district_name_hi": "गुवाहाटी", "state_code": "AS", "state_name": "Assam"},
        {"district_code": "AS002", "district_name": "Dibrugarh", "district_name_hi": "डिब्रूगढ़", "state_code": "AS", "state_name": "Assam"},
        {"district_code": "AS003", "district_name": "Silchar", "district_name_hi": "सिलचर", "state_code": "AS", "state_name": "Assam"},
        {"district_code": "AS004", "district_name": "Jorhat", "district_name_hi": "जोरहाट", "state_code": "AS", "state_name": "Assam"},
        
        # Bihar
        {"district_code": "BR001", "district_name": "Patna", "district_name_hi": "पटना", "state_code": "BR", "state_name": "Bihar"},
        {"district_code": "BR002", "district_name": "Gaya", "district_name_hi": "गया", "state_code": "BR", "state_name": "Bihar"},
        {"district_code": "BR003", "district_name": "Muzaffarpur", "district_name_hi": "मुजफ्फरपुर", "state_code": "BR", "state_name": "Bihar"},
        {"district_code": "BR004", "district_name": "Bhagalpur", "district_name_hi": "भागलपुर", "state_code": "BR", "state_name": "Bihar"},
        {"district_code": "BR005", "district_name": "Darbhanga", "district_name_hi": "दरभंगा", "state_code": "BR", "state_name": "Bihar"},
        
        # Chhattisgarh
        {"district_code": "CT001", "district_name": "Raipur", "district_name_hi": "रायपुर", "state_code": "CT", "state_name": "Chhattisgarh"},
        {"district_code": "CT002", "district_name": "Bilaspur", "district_name_hi": "बिलासपुर", "state_code": "CT", "state_name": "Chhattisgarh"},
        {"district_code": "CT003", "district_name": "Durg", "district_name_hi": "दुर्ग", "state_code": "CT", "state_name": "Chhattisgarh"},
        {"district_code": "CT004", "district_name": "Korba", "district_name_hi": "कोरबा", "state_code": "CT", "state_name": "Chhattisgarh"},
        
        # Goa
        {"district_code": "GA001", "district_name": "North Goa", "district_name_hi": "उत्तर गोवा", "state_code": "GA", "state_name": "Goa"},
        {"district_code": "GA002", "district_name": "South Goa", "district_name_hi": "दक्षिण गोवा", "state_code": "GA", "state_name": "Goa"},
        
        # Gujarat
        {"district_code": "GJ001", "district_name": "Ahmedabad", "district_name_hi": "अहमदाबाद", "state_code": "GJ", "state_name": "Gujarat"},
        {"district_code": "GJ002", "district_name": "Surat", "district_name_hi": "सूरत", "state_code": "GJ", "state_name": "Gujarat"},
        {"district_code": "GJ003", "district_name": "Vadodara", "district_name_hi": "वडोदरा", "state_code": "GJ", "state_name": "Gujarat"},
        {"district_code": "GJ004", "district_name": "Rajkot", "district_name_hi": "राजकोट", "state_code": "GJ", "state_name": "Gujarat"},
        {"district_code": "GJ005", "district_name": "Bhavnagar", "district_name_hi": "भावनगर", "state_code": "GJ", "state_name": "Gujarat"},
        
        # Haryana
        {"district_code": "HR001", "district_name": "Gurugram", "district_name_hi": "गुरुग्राम", "state_code": "HR", "state_name": "Haryana"},
        {"district_code": "HR002", "district_name": "Faridabad", "district_name_hi": "फरीदाबाद", "state_code": "HR", "state_name": "Haryana"},
        {"district_code": "HR003", "district_name": "Panipat", "district_name_hi": "पानीपत", "state_code": "HR", "state_name": "Haryana"},
        {"district_code": "HR004", "district_name": "Ambala", "district_name_hi": "अंबाला", "state_code": "HR", "state_name": "Haryana"},
        
        # Himachal Pradesh
        {"district_code": "HP001", "district_name": "Shimla", "district_name_hi": "शिमला", "state_code": "HP", "state_name": "Himachal Pradesh"},
        {"district_code": "HP002", "district_name": "Kangra", "district_name_hi": "कांगड़ा", "state_code": "HP", "state_name": "Himachal Pradesh"},
        {"district_code": "HP003", "district_name": "Mandi", "district_name_hi": "मंडी", "state_code": "HP", "state_name": "Himachal Pradesh"},
        
        # Jharkhand
        {"district_code": "JH001", "district_name": "Ranchi", "district_name_hi": "रांची", "state_code": "JH", "state_name": "Jharkhand"},
        {"district_code": "JH002", "district_name": "Jamshedpur", "district_name_hi": "जमशेदपुर", "state_code": "JH", "state_name": "Jharkhand"},
        {"district_code": "JH003", "district_name": "Dhanbad", "district_name_hi": "धनबाद", "state_code": "JH", "state_name": "Jharkhand"},
        {"district_code": "JH004", "district_name": "Bokaro", "district_name_hi": "बोकारो", "state_code": "JH", "state_name": "Jharkhand"},
        
        # Karnataka
        {"district_code": "KA001", "district_name": "Bangalore", "district_name_hi": "बैंगलोर", "state_code": "KA", "state_name": "Karnataka"},
        {"district_code": "KA002", "district_name": "Mysore", "district_name_hi": "मैसूर", "state_code": "KA", "state_name": "Karnataka"},
        {"district_code": "KA003", "district_name": "Mangalore", "district_name_hi": "मंगलौर", "state_code": "KA", "state_name": "Karnataka"},
        {"district_code": "KA004", "district_name": "Hubli", "district_name_hi": "हुबली", "state_code": "KA", "state_name": "Karnataka"},
        
        # Kerala
        {"district_code": "KL001", "district_name": "Thiruvananthapuram", "district_name_hi": "तिरुवनंतपुरम", "state_code": "KL", "state_name": "Kerala"},
        {"district_code": "KL002", "district_name": "Kochi", "district_name_hi": "कोच्चि", "state_code": "KL", "state_name": "Kerala"},
        {"district_code": "KL003", "district_name": "Kozhikode", "district_name_hi": "कोझिकोड", "state_code": "KL", "state_name": "Kerala"},
        {"district_code": "KL004", "district_name": "Kollam", "district_name_hi": "कोल्लम", "state_code": "KL", "state_name": "Kerala"},
        
        # Madhya Pradesh
        {"district_code": "MP001", "district_name": "Bhopal", "district_name_hi": "भोपाल", "state_code": "MP", "state_name": "Madhya Pradesh"},
        {"district_code": "MP002", "district_name": "Indore", "district_name_hi": "इंदौर", "state_code": "MP", "state_name": "Madhya Pradesh"},
        {"district_code": "MP003", "district_name": "Jabalpur", "district_name_hi": "जबलपुर", "state_code": "MP", "state_name": "Madhya Pradesh"},
        {"district_code": "MP004", "district_name": "Gwalior", "district_name_hi": "ग्वालियर", "state_code": "MP", "state_name": "Madhya Pradesh"},
        {"district_code": "MP005", "district_name": "Ujjain", "district_name_hi": "उज्जैन", "state_code": "MP", "state_name": "Madhya Pradesh"},
        
        # Maharashtra
        {"district_code": "MH001", "district_name": "Mumbai", "district_name_hi": "मुंबई", "state_code": "MH", "state_name": "Maharashtra"},
        {"district_code": "MH002", "district_name": "Pune", "district_name_hi": "पुणे", "state_code": "MH", "state_name": "Maharashtra"},
        {"district_code": "MH003", "district_name": "Nagpur", "district_name_hi": "नागपुर", "state_code": "MH", "state_name": "Maharashtra"},
        {"district_code": "MH004", "district_name": "Nashik", "district_name_hi": "नासिक", "state_code": "MH", "state_name": "Maharashtra"},
        {"district_code": "MH005", "district_name": "Aurangabad", "district_name_hi": "औरंगाबाद", "state_code": "MH", "state_name": "Maharashtra"},
        
        # Manipur
        {"district_code": "MN001", "district_name": "Imphal West", "district_name_hi": "इंफाल पश्चिम", "state_code": "MN", "state_name": "Manipur"},
        {"district_code": "MN002", "district_name": "Imphal East", "district_name_hi": "इंफाल पूर्व", "state_code": "MN", "state_name": "Manipur"},
        {"district_code": "MN003", "district_name": "Thoubal", "district_name_hi": "थौबल", "state_code": "MN", "state_name": "Manipur"},
        
        # Meghalaya
        {"district_code": "ML001", "district_name": "Shillong", "district_name_hi": "शिलांग", "state_code": "ML", "state_name": "Meghalaya"},
        {"district_code": "ML002", "district_name": "Tura", "district_name_hi": "तुरा", "state_code": "ML", "state_name": "Meghalaya"},
        
        # Mizoram
        {"district_code": "MZ001", "district_name": "Aizawl", "district_name_hi": "आइजोल", "state_code": "MZ", "state_name": "Mizoram"},
        {"district_code": "MZ002", "district_name": "Lunglei", "district_name_hi": "लुंगलेई", "state_code": "MZ", "state_name": "Mizoram"},
        
        # Nagaland
        {"district_code": "NL001", "district_name": "Kohima", "district_name_hi": "कोहिमा", "state_code": "NL", "state_name": "Nagaland"},
        {"district_code": "NL002", "district_name": "Dimapur", "district_name_hi": "दीमापुर", "state_code": "NL", "state_name": "Nagaland"},
        
        # Odisha
        {"district_code": "OR001", "district_name": "Bhubaneswar", "district_name_hi": "भुवनेश्वर", "state_code": "OR", "state_name": "Odisha"},
        {"district_code": "OR002", "district_name": "Cuttack", "district_name_hi": "कटक", "state_code": "OR", "state_name": "Odisha"},
        {"district_code": "OR003", "district_name": "Rourkela", "district_name_hi": "राउरकेला", "state_code": "OR", "state_name": "Odisha"},
        {"district_code": "OR004", "district_name": "Puri", "district_name_hi": "पुरी", "state_code": "OR", "state_name": "Odisha"},
        
        # Punjab
        {"district_code": "PB001", "district_name": "Ludhiana", "district_name_hi": "लुधियाना", "state_code": "PB", "state_name": "Punjab"},
        {"district_code": "PB002", "district_name": "Amritsar", "district_name_hi": "अमृतसर", "state_code": "PB", "state_name": "Punjab"},
        {"district_code": "PB003", "district_name": "Jalandhar", "district_name_hi": "जालंधर", "state_code": "PB", "state_name": "Punjab"},
        {"district_code": "PB004", "district_name": "Patiala", "district_name_hi": "पटियाला", "state_code": "PB", "state_name": "Punjab"},
        
        # Rajasthan
        {"district_code": "RJ001", "district_name": "Jaipur", "district_name_hi": "जयपुर", "state_code": "RJ", "state_name": "Rajasthan"},
        {"district_code": "RJ002", "district_name": "Jodhpur", "district_name_hi": "जोधपुर", "state_code": "RJ", "state_name": "Rajasthan"},
        {"district_code": "RJ003", "district_name": "Udaipur", "district_name_hi": "उदयपुर", "state_code": "RJ", "state_name": "Rajasthan"},
        {"district_code": "RJ004", "district_name": "Kota", "district_name_hi": "कोटा", "state_code": "RJ", "state_name": "Rajasthan"},
        {"district_code": "RJ005", "district_name": "Ajmer", "district_name_hi": "अजमेर", "state_code": "RJ", "state_name": "Rajasthan"},
        
        # Sikkim
        {"district_code": "SK001", "district_name": "Gangtok", "district_name_hi": "गंगटोक", "state_code": "SK", "state_name": "Sikkim"},
        {"district_code": "SK002", "district_name": "Namchi", "district_name_hi": "नामची", "state_code": "SK", "state_name": "Sikkim"},
        
        # Tamil Nadu
        {"district_code": "TN001", "district_name": "Chennai", "district_name_hi": "चेन्नई", "state_code": "TN", "state_name": "Tamil Nadu"},
        {"district_code": "TN002", "district_name": "Coimbatore", "district_name_hi": "कोयंबटूर", "state_code": "TN", "state_name": "Tamil Nadu"},
        {"district_code": "TN003", "district_name": "Madurai", "district_name_hi": "मदुरै", "state_code": "TN", "state_name": "Tamil Nadu"},
        {"district_code": "TN004", "district_name": "Trichy", "district_name_hi": "तिरुचि", "state_code": "TN", "state_name": "Tamil Nadu"},
        {"district_code": "TN005", "district_name": "Salem", "district_name_hi": "सेलम", "state_code": "TN", "state_name": "Tamil Nadu"},
        
        # Telangana
        {"district_code": "TG001", "district_name": "Hyderabad", "district_name_hi": "हैदराबाद", "state_code": "TG", "state_name": "Telangana"},
        {"district_code": "TG002", "district_name": "Warangal", "district_name_hi": "वारंगल", "state_code": "TG", "state_name": "Telangana"},
        {"district_code": "TG003", "district_name": "Nizamabad", "district_name_hi": "निज़ामाबाद", "state_code": "TG", "state_name": "Telangana"},
        {"district_code": "TG004", "district_name": "Khammam", "district_name_hi": "खम्मम", "state_code": "TG", "state_name": "Telangana"},
        
        # Tripura
        {"district_code": "TR001", "district_name": "Agartala", "district_name_hi": "अगरतला", "state_code": "TR", "state_name": "Tripura"},
        {"district_code": "TR002", "district_name": "Udaipur", "district_name_hi": "उदयपुर", "state_code": "TR", "state_name": "Tripura"},
        
        # Uttar Pradesh
        {"district_code": "UP001", "district_name": "Lucknow", "district_name_hi": "लखनऊ", "state_code": "UP", "state_name": "Uttar Pradesh"},
        {"district_code": "UP002", "district_name": "Kanpur", "district_name_hi": "कानपुर", "state_code": "UP", "state_name": "Uttar Pradesh"},
        {"district_code": "UP003", "district_name": "Varanasi", "district_name_hi": "वाराणसी", "state_code": "UP", "state_name": "Uttar Pradesh"},
        {"district_code": "UP004", "district_name": "Prayagraj", "district_name_hi": "प्रयागराज", "state_code": "UP", "state_name": "Uttar Pradesh"},
        {"district_code": "UP005", "district_name": "Agra", "district_name_hi": "आगरा", "state_code": "UP", "state_name": "Uttar Pradesh"},
        {"district_code": "UP006", "district_name": "Meerut", "district_name_hi": "मेरठ", "state_code": "UP", "state_name": "Uttar Pradesh"},
        {"district_code": "UP007", "district_name": "Noida", "district_name_hi": "नोएडा", "state_code": "UP", "state_name": "Uttar Pradesh"},
        
        # Uttarakhand
        {"district_code": "UT001", "district_name": "Dehradun", "district_name_hi": "देहरादून", "state_code": "UT", "state_name": "Uttarakhand"},
        {"district_code": "UT002", "district_name": "Haridwar", "district_name_hi": "हरिद्वार", "state_code": "UT", "state_name": "Uttarakhand"},
        {"district_code": "UT003", "district_name": "Nainital", "district_name_hi": "नैनीताल", "state_code": "UT", "state_name": "Uttarakhand"},
        
        # West Bengal
        {"district_code": "WB001", "district_name": "Kolkata", "district_name_hi": "कोलकाता", "state_code": "WB", "state_name": "West Bengal"},
        {"district_code": "WB002", "district_name": "Darjeeling", "district_name_hi": "दार्जिलिंग", "state_code": "WB", "state_name": "West Bengal"},
        {"district_code": "WB003", "district_name": "Howrah", "district_name_hi": "हावड़ा", "state_code": "WB", "state_name": "West Bengal"},
        {"district_code": "WB004", "district_name": "Siliguri", "district_name_hi": "सिलीगुड़ी", "state_code": "WB", "state_name": "West Bengal"},
    ]
    
    # Insert states and districts
    await db.states.delete_many({})
    await db.districts.delete_many({})
    await db.states.insert_many(states)
    await db.districts.insert_many(districts)
    
    # Generate performance data for last 12 months
    await db.performances.delete_many({})
    performances = []
    
    current_year = 2025
    current_month = 10
    
    for district in districts:
        for month_offset in range(12):
            month = current_month - month_offset
            year = current_year
            
            if month <= 0:
                month += 12
                year -= 1
            
            # Generate realistic random data
            total_job_cards = random.randint(20000, 100000)
            active_job_cards = int(total_job_cards * random.uniform(0.6, 0.8))
            total_workers = int(total_job_cards * random.uniform(1.5, 2.5))
            active_workers = int(active_job_cards * random.uniform(1.5, 2.5))
            person_days = random.randint(100000, 500000)
            
            total_budget = random.uniform(5000000, 50000000)
            expenditure = total_budget * random.uniform(0.7, 0.95)
            
            total_works = random.randint(200, 1000)
            completed = int(total_works * random.uniform(0.6, 0.8))
            
            perf = {
                "id": str(uuid.uuid4()),
                "state_code": district["state_code"],
                "state_name": district["state_name"],
                "district_code": district["district_code"],
                "district_name": district["district_name"],
                "month": month,
                "year": year,
                "total_job_cards": total_job_cards,
                "active_job_cards": active_job_cards,
                "total_workers": total_workers,
                "active_workers": active_workers,
                "person_days_generated": person_days,
                "average_days_per_household": round(person_days / active_job_cards, 2),
                "women_person_days": int(person_days * random.uniform(0.45, 0.55)),
                "sc_person_days": int(person_days * random.uniform(0.15, 0.25)),
                "st_person_days": int(person_days * random.uniform(0.10, 0.20)),
                "total_budget_allocated": round(total_budget, 2),
                "total_expenditure": round(expenditure, 2),
                "wage_expenditure": round(expenditure * 0.6, 2),
                "material_expenditure": round(expenditure * 0.4, 2),
                "average_wage_per_day": round(random.uniform(200, 350), 2),
                "total_works": total_works,
                "completed_works": completed,
                "ongoing_works": total_works - completed,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            performances.append(perf)
    
    if performances:
        await db.performances.insert_many(performances)


# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
