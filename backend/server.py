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
    
    # Sample states
    states = [
        {"state_code": "UP", "state_name": "Uttar Pradesh", "state_name_hi": "उत्तर प्रदेश"},
        {"state_code": "MH", "state_name": "Maharashtra", "state_name_hi": "महाराष्ट्र"},
        {"state_code": "BR", "state_name": "Bihar", "state_name_hi": "बिहार"},
        {"state_code": "WB", "state_name": "West Bengal", "state_name_hi": "पश्चिम बंगाल"},
        {"state_code": "MP", "state_name": "Madhya Pradesh", "state_name_hi": "मध्य प्रदेश"},
        {"state_code": "TN", "state_name": "Tamil Nadu", "state_name_hi": "तमिलनाडु"},
        {"state_code": "RJ", "state_name": "Rajasthan", "state_name_hi": "राजस्थान"},
        {"state_code": "KA", "state_name": "Karnataka", "state_name_hi": "कर्नाटक"},
    ]
    
    # Sample districts
    districts = [
        # UP districts
        {"district_code": "UP001", "district_name": "Lucknow", "district_name_hi": "लखनऊ", "state_code": "UP", "state_name": "Uttar Pradesh"},
        {"district_code": "UP002", "district_name": "Kanpur", "district_name_hi": "कानपुर", "state_code": "UP", "state_name": "Uttar Pradesh"},
        {"district_code": "UP003", "district_name": "Varanasi", "district_name_hi": "वाराणसी", "state_code": "UP", "state_name": "Uttar Pradesh"},
        {"district_code": "UP004", "district_name": "Allahabad", "district_name_hi": "इलाहाबाद", "state_code": "UP", "state_name": "Uttar Pradesh"},
        # MH districts
        {"district_code": "MH001", "district_name": "Mumbai", "district_name_hi": "मुंबई", "state_code": "MH", "state_name": "Maharashtra"},
        {"district_code": "MH002", "district_name": "Pune", "district_name_hi": "पुणे", "state_code": "MH", "state_name": "Maharashtra"},
        {"district_code": "MH003", "district_name": "Nagpur", "district_name_hi": "नागपुर", "state_code": "MH", "state_name": "Maharashtra"},
        # BR districts
        {"district_code": "BR001", "district_name": "Patna", "district_name_hi": "पटना", "state_code": "BR", "state_name": "Bihar"},
        {"district_code": "BR002", "district_name": "Gaya", "district_name_hi": "गया", "state_code": "BR", "state_name": "Bihar"},
        {"district_code": "BR003", "district_name": "Muzaffarpur", "district_name_hi": "मुजफ्फरपुर", "state_code": "BR", "state_name": "Bihar"},
        # WB districts
        {"district_code": "WB001", "district_name": "Kolkata", "district_name_hi": "कोलकाता", "state_code": "WB", "state_name": "West Bengal"},
        {"district_code": "WB002", "district_name": "Darjeeling", "district_name_hi": "दार्जिलिंग", "state_code": "WB", "state_name": "West Bengal"},
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
