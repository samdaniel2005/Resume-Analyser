"""SignalRank Resume Screening API."""
from fastapi import FastAPI, APIRouter, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import io
import csv
import uuid
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

from scoring import (
    score_resume,
    determine_status,
    calculate_breakdown,
    DEFAULT_SETTINGS,
    CATEGORY_LABELS,
)

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / ".env")

UPLOAD_DIR = ROOT_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

mongo_url = os.environ["MONGO_URL"]
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ["DB_NAME"]]

app = FastAPI(title="SignalRank API")
api_router = APIRouter(prefix="/api")

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


# ─────────────── Models ───────────────
class ScoreBreakdown(BaseModel):
    model_config = ConfigDict(extra="ignore")
    core_tech: int = 0
    ml_de_tools: int = 0
    cloud_mlops: int = 0
    education: int = 0
    experience: int = 0
    projects_opensource: int = 0
    certs_research: int = 0
    leadership_soft: int = 0
    penalty: int = 0
    total: int = 0


class Candidate(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: str = ""
    phone: str = ""
    filename: str
    stored_filename: str
    final_score: int
    status: str
    breakdown: ScoreBreakdown
    extracted_text: str = ""
    decision: Optional[str] = None  # recruiter override
    uploaded_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class CandidateSummary(BaseModel):
    id: str
    name: str
    email: str
    filename: str
    final_score: int
    status: str
    decision: Optional[str] = None
    breakdown: ScoreBreakdown
    uploaded_at: str


class SettingsModel(BaseModel):
    weights: Dict[str, int]
    keywords: Dict[str, List[str]]
    thresholds: Dict[str, int]


class DecisionUpdate(BaseModel):
    decision: str  # "selected" | "rejected" | "hold" | ""


# ─────────────── Settings helpers ───────────────
SETTINGS_DOC_ID = "global"


async def get_settings() -> dict:
    doc = await db.settings.find_one({"_id": SETTINGS_DOC_ID})
    if not doc:
        await db.settings.insert_one({"_id": SETTINGS_DOC_ID, **DEFAULT_SETTINGS})
        return DEFAULT_SETTINGS
    doc.pop("_id", None)
    # Merge in any missing default keys (forward-compat)
    for k, v in DEFAULT_SETTINGS.items():
        doc.setdefault(k, v)
    return doc


# ─────────────── Routes ───────────────
@api_router.get("/")
async def root():
    return {"service": "SignalRank", "status": "ok"}


@api_router.get("/categories")
async def get_categories():
    return CATEGORY_LABELS


@api_router.get("/settings", response_model=SettingsModel)
async def settings_get():
    s = await get_settings()
    return SettingsModel(**s)


@api_router.put("/settings", response_model=SettingsModel)
async def settings_put(payload: SettingsModel):
    data = payload.model_dump()
    await db.settings.update_one(
        {"_id": SETTINGS_DOC_ID},
        {"$set": data},
        upsert=True,
    )
    return payload


@api_router.post("/settings/reset", response_model=SettingsModel)
async def settings_reset():
    await db.settings.update_one(
        {"_id": SETTINGS_DOC_ID},
        {"$set": DEFAULT_SETTINGS},
        upsert=True,
    )
    return SettingsModel(**DEFAULT_SETTINGS)


@api_router.post("/resumes/upload")
async def upload_resumes(files: List[UploadFile] = File(...)):
    settings = await get_settings()
    results = []
    errors = []

    for f in files:
        try:
            content = await f.read()
            if not content:
                errors.append({"filename": f.filename, "error": "Empty file"})
                continue

            ext = Path(f.filename).suffix.lower()
            if ext not in [".pdf", ".png", ".jpg", ".jpeg", ".webp", ".tiff", ".bmp"]:
                errors.append({"filename": f.filename, "error": f"Unsupported file type: {ext}"})
                continue

            scored = score_resume(content, f.filename, settings)

            stored_name = f"{uuid.uuid4()}{ext}"
            (UPLOAD_DIR / stored_name).write_bytes(content)

            cand = Candidate(
                name=scored["name"],
                email=scored["email"],
                phone=scored["phone"],
                filename=f.filename,
                stored_filename=stored_name,
                final_score=scored["final_score"],
                status=scored["status"],
                breakdown=ScoreBreakdown(**scored["breakdown"]),
                extracted_text=scored["extracted_text"],
            )
            doc = cand.model_dump()
            await db.candidates.insert_one(doc)
            results.append({
                "id": cand.id,
                "name": cand.name,
                "filename": cand.filename,
                "final_score": cand.final_score,
                "status": cand.status,
            })
        except Exception as e:
            logger.exception("Failed to process resume %s", f.filename)
            errors.append({"filename": f.filename, "error": str(e)})

    return {"processed": results, "errors": errors}


@api_router.get("/resumes", response_model=List[CandidateSummary])
async def list_resumes(status: Optional[str] = None, q: Optional[str] = None):
    query: Dict[str, Any] = {}
    if status:
        query["status"] = status
    if q:
        query["$or"] = [
            {"name": {"$regex": q, "$options": "i"}},
            {"email": {"$regex": q, "$options": "i"}},
            {"filename": {"$regex": q, "$options": "i"}},
        ]

    cursor = db.candidates.find(query, {"_id": 0, "extracted_text": 0}).sort("final_score", -1)
    items = await cursor.to_list(length=1000)
    return [CandidateSummary(**it) for it in items]


@api_router.get("/resumes/stats")
async def resumes_stats():
    cursor = db.candidates.find({}, {"_id": 0, "status": 1, "final_score": 1})
    items = await cursor.to_list(length=10000)
    total = len(items)
    avg_score = round(sum(i["final_score"] for i in items) / total, 1) if total else 0
    counts = {"Fast Track": 0, "Shortlist": 0, "Review": 0, "Rejected": 0}
    for i in items:
        counts[i["status"]] = counts.get(i["status"], 0) + 1
    return {
        "total": total,
        "avg_score": avg_score,
        "fast_track": counts.get("Fast Track", 0),
        "shortlist": counts.get("Shortlist", 0),
        "review": counts.get("Review", 0),
        "rejected": counts.get("Rejected", 0),
    }


@api_router.get("/resumes/export")
async def export_shortlisted():
    cursor = db.candidates.find(
        {"status": {"$in": ["Fast Track", "Shortlist"]}},
        {"_id": 0, "extracted_text": 0},
    ).sort("final_score", -1)
    items = await cursor.to_list(length=10000)

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow([
        "rank", "name", "email", "phone", "filename", "status",
        "final_score", "core_tech", "ml_de_tools", "cloud_mlops",
        "education", "experience", "projects_opensource",
        "certs_research", "leadership_soft", "penalty",
    ])
    for i, c in enumerate(items, start=1):
        b = c["breakdown"]
        writer.writerow([
            i, c["name"], c.get("email", ""), c.get("phone", ""),
            c["filename"], c["status"], c["final_score"],
            b["core_tech"], b["ml_de_tools"], b["cloud_mlops"],
            b["education"], b["experience"], b["projects_opensource"],
            b["certs_research"], b["leadership_soft"], b["penalty"],
        ])
    buf.seek(0)
    return StreamingResponse(
        iter([buf.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=shortlisted_candidates.csv"},
    )


@api_router.get("/resumes/{candidate_id}", response_model=Candidate)
async def get_resume(candidate_id: str):
    doc = await db.candidates.find_one({"id": candidate_id}, {"_id": 0})
    if not doc:
        raise HTTPException(404, "Candidate not found")
    return Candidate(**doc)


@api_router.patch("/resumes/{candidate_id}/decision", response_model=Candidate)
async def update_decision(candidate_id: str, payload: DecisionUpdate):
    res = await db.candidates.update_one(
        {"id": candidate_id},
        {"$set": {"decision": payload.decision}},
    )
    if res.matched_count == 0:
        raise HTTPException(404, "Candidate not found")
    doc = await db.candidates.find_one({"id": candidate_id}, {"_id": 0})
    return Candidate(**doc)


@api_router.delete("/resumes/{candidate_id}")
async def delete_resume(candidate_id: str):
    doc = await db.candidates.find_one({"id": candidate_id}, {"_id": 0})
    if not doc:
        raise HTTPException(404, "Candidate not found")
    try:
        (UPLOAD_DIR / doc["stored_filename"]).unlink(missing_ok=True)
    except Exception:
        pass
    await db.candidates.delete_one({"id": candidate_id})
    return {"deleted": candidate_id}


@api_router.post("/resumes/rescore")
async def rescore_all():
    """Re-score all existing candidates with current settings."""
    settings = await get_settings()
    cursor = db.candidates.find({}, {"_id": 0})
    updated = 0
    async for doc in cursor:
        text = doc.get("extracted_text", "")
        breakdown = calculate_breakdown(text, settings)
        status = determine_status(breakdown["total"], settings["thresholds"])
        await db.candidates.update_one(
            {"id": doc["id"]},
            {"$set": {
                "breakdown": breakdown,
                "final_score": breakdown["total"],
                "status": status,
            }},
        )
        updated += 1
    return {"updated": updated}


app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get("CORS_ORIGINS", "*").split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
