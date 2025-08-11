from fastapi import FastAPI, APIRouter, HTTPException, Request, Query
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
import uuid
from datetime import datetime, timedelta
from pymongo.errors import DuplicateKeyError


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db_name = os.environ.get('DB_NAME', 'app_db')
db = client[db_name]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# ----------------------
# Models
# ----------------------
class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheckCreate(BaseModel):
    client_name: str

class Palette(BaseModel):
    id: str
    name: str
    bg: str
    color: str
    baseBg: str
    baseColor: str
    accent: str
    subtle: str

class PreferenceIn(BaseModel):
    palette_id: str
    session_id: Optional[str] = None

class PreferenceOut(BaseModel):
    session_id: str
    palette_id: str
    updated_at: datetime

class NotifyIn(BaseModel):
    email: EmailStr

class EmailOut(BaseModel):
    email: EmailStr
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# ----------------------
# Seed Palettes and Indexes
# ----------------------
CURATED_PALETTES: List[Palette] = [
    Palette(id="arctic", name="Arctic", bg="#F5F7F9", color="#191e22", baseBg="#000000", baseColor="#ffffff", accent="#2a454c", subtle="#637281"),
    Palette(id="azure", name="Azure", bg="#EAF2F8", color="#1c2b36", baseBg="#000000", baseColor="#ffffff", accent="#2D6E9D", subtle="#6C8597"),
    Palette(id="indigo", name="Indigo", bg="#EEF0FA", color="#1f2430", baseBg="#000000", baseColor="#ffffff", accent="#434A9F", subtle="#6B6F9C"),
    Palette(id="scarlet", name="Scarlet", bg="#FFF1F1", color="#23191b", baseBg="#000000", baseColor="#ffffff", accent="#B23B3B", subtle="#8C5C5C"),
    Palette(id="mandarin", name="Mandarin", bg="#FFF6EC", color="#271f17", baseBg="#000000", baseColor="#ffffff", accent="#D77E3E", subtle="#9B6C4F"),
    Palette(id="mint", name="Mint", bg="#ECF8F3", color="#14201b", baseBg="#000000", baseColor="#ffffff", accent="#3AA483", subtle="#628A7C"),
    Palette(id="forest", name="Forest", bg="#F3F6F4", color="#172017", baseBg="#000000", baseColor="#ffffff", accent="#355A3C", subtle="#6A7A6D"),
    Palette(id="charcoal", name="Charcoal", bg="#F2F3F5", color="#202226", baseBg="#000000", baseColor="#ffffff", accent="#2C2F36", subtle="#6E7480"),
    Palette(id="sand", name="Sand", bg="#FAF7F2", color="#2b2620", baseBg="#000000", baseColor="#ffffff", accent="#B8A07A", subtle="#8B8072"),
]

async def ensure_indexes_and_seed():
    # Indexes
    await db.preferences.create_index("session_id", unique=True)
    await db.notify_emails.create_index("email", unique=True)
    await db.palettes.create_index("id", unique=True)
    # TTL for rate limits
    await db.rate_limits.create_index("expireAt", expireAfterSeconds=0)

    # Seed palettes if empty
    count = await db.palettes.count_documents({})
    if count == 0:
        docs = [
            {"_id": p.id, **p.model_dump()} for p in CURATED_PALETTES
        ]
        await db.palettes.insert_many(docs)
        logger.info("Seeded curated palettes")


@app.on_event("startup")
async def startup_tasks():
    await ensure_indexes_and_seed()


# ----------------------
# Routes (existing)
# ----------------------
@api_router.get("/")
async def root():
    return {"message": "Hello World"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.dict()
    status_obj = StatusCheck(**status_dict)
    _ = await db.status_checks.insert_one(status_obj.dict())
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find().to_list(1000)
    return [StatusCheck(**status_check) for status_check in status_checks]


# ----------------------
# New/Updated Routes
# ----------------------
@api_router.get("/palettes", response_model=List[Palette])
async def get_palettes():
    items = await db.palettes.find({}, {"_id": 0}).to_list(1000)
    return [Palette(**item) for item in items]

@api_router.post("/preferences", response_model=PreferenceOut)
async def save_preference(body: PreferenceIn):
    # Validate palette exists
    palette = await db.palettes.find_one({"id": body.palette_id})
    if not palette:
        raise HTTPException(status_code=404, detail="Palette not found")

    session_id = body.session_id or str(uuid.uuid4())
    now = datetime.utcnow()
    await db.preferences.update_one(
        {"session_id": session_id},
        {"$set": {"session_id": session_id, "palette_id": body.palette_id, "updated_at": now}},
        upsert=True,
    )
    return PreferenceOut(session_id=session_id, palette_id=body.palette_id, updated_at=now)

@api_router.get("/preferences", response_model=PreferenceOut)
async def load_preference(session_id: str = Query(...)):
    pref = await db.preferences.find_one({"session_id": session_id})
    if not pref:
        raise HTTPException(status_code=404, detail="Preference not found")
    return PreferenceOut(session_id=pref["session_id"], palette_id=pref["palette_id"], updated_at=pref.get("updated_at", datetime.utcnow()))


def _client_ip(request: Request) -> str:
    # Prefer X-Forwarded-For (K8s/Ingress) then fall back to client host
    xff = request.headers.get("x-forwarded-for") or request.headers.get("X-Forwarded-For")
    if xff:
        # get first IP in the list
        return xff.split(",")[0].strip()
    return request.client.host if request.client else "unknown"

async def _rate_limit(key: str, window_seconds: int = 60):
    now = datetime.utcnow()
    expire_at = now + timedelta(seconds=window_seconds)
    try:
        await db.rate_limits.insert_one({"_id": key, "expireAt": expire_at})
        return True
    except DuplicateKeyError:
        return False

@api_router.post("/notify")
async def notify(body: NotifyIn, request: Request):
    # Rate limit: 1/min per IP and per email
    ip = _client_ip(request)
    email_key = f"notify:email:{body.email.lower()}"
    ip_key = f"notify:ip:{ip}"

    ok_email = await _rate_limit(email_key, 60)
    ok_ip = await _rate_limit(ip_key, 60)
    if not (ok_email and ok_ip):
        raise HTTPException(status_code=429, detail="Too many requests. Please try again in a minute.")

    now = datetime.utcnow()
    await db.notify_emails.update_one(
        {"email": body.email},
        {"$setOnInsert": {"created_at": now}, "$set": {"updated_at": now}},
        upsert=True,
    )
    return {"status": "ok"}

@api_router.get("/admin/emails", response_model=List[EmailOut])
async def admin_list_emails():
    items = await db.notify_emails.find({}, {"_id": 0}).to_list(10000)
    return [EmailOut(**item) for item in items]


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