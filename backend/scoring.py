"""Resume scoring engine - adapted from main.py.

OCR extraction + weighted keyword heuristic scoring across 8 categories.
Total ~125 points. Status buckets: Fast Track / Shortlist / Review / Rejected.
"""
import re
import io
from pathlib import Path
import cv2
import numpy as np
import pytesseract
from PIL import Image
from pdf2image import convert_from_bytes


# Default scoring configuration (editable via Settings API)
DEFAULT_SETTINGS = {
    "weights": {
        "core_tech": 30,
        "ml_de_tools": 20,
        "cloud_mlops": 15,
        "education": 15,
        "experience": 20,
        "projects_opensource": 10,
        "certs_research": 10,
        "leadership_soft": 5,
    },
    "keywords": {
        "core_languages": ["python", "java", "scala", "r ", "c++", "go ", "julia"],
        "ml_frameworks": ["tensorflow", "pytorch", "scikit-learn", "keras", "xgboost", "lightgbm", "hugging face"],
        "data_tools": ["spark", "kafka", "airflow", "dbt", "hadoop", "flink", "luigi", "prefect", "dagster"],
        "viz_tools": ["tableau", "power bi", "looker", "matplotlib", "seaborn", "plotly"],
        "cloud_platforms": ["aws", "azure", "gcp", "google cloud"],
        "mlops_tools": ["mlflow", "kubeflow", "sagemaker", "vertex ai", "docker", "kubernetes", "ci/cd", "jenkins", "github actions"],
        "tier1_institutes": ["iit", "iim", "mit", "stanford", "harvard", "cmu", "oxford", "cambridge", "nit", "bits"],
        "senior_roles": ["senior", "lead", "principal", "staff engineer", "head of", "director", "manager", "architect"],
        "recognized_certs": ["aws certified", "google certified", "azure certified", "tensorflow certificate", "databricks", "coursera", "udacity nanodegree", "professional certificate"],
        "leadership_kw": ["team lead", "mentored", "mentoring", "managed a team", "agile", "scrum", "cross-functional", "stakeholder"],
    },
    "thresholds": {
        "fast_track": 75,
        "shortlist": 55,
        "review": 35,
    },
}

CATEGORY_LABELS = {
    "core_tech": "Core Technical Skills",
    "ml_de_tools": "ML / Data Engineering Tools",
    "cloud_mlops": "Cloud & MLOps",
    "education": "Education",
    "experience": "Experience Depth",
    "projects_opensource": "Projects & Open Source",
    "certs_research": "Certifications & Research",
    "leadership_soft": "Leadership & Soft Skills",
}


def _ocr_image_array(img: np.ndarray) -> str:
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    _, gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return pytesseract.image_to_string(gray)


def extract_text(file_bytes: bytes, filename: str) -> str:
    """Extract text from image or PDF bytes."""
    ext = Path(filename).suffix.lower()
    text_parts = []

    if ext == ".pdf":
        try:
            pages = convert_from_bytes(file_bytes, dpi=200)
        except Exception:
            return ""
        for page in pages:
            arr = cv2.cvtColor(np.array(page), cv2.COLOR_RGB2BGR)
            text_parts.append(_ocr_image_array(arr))
    else:
        try:
            pil = Image.open(io.BytesIO(file_bytes)).convert("RGB")
        except Exception:
            return ""
        arr = cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR)
        text_parts.append(_ocr_image_array(arr))

    return "\n".join(text_parts).lower()


def _extract_candidate_name(text: str, fallback_filename: str) -> str:
    """Try to extract candidate name from the first lines of resume."""
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    for ln in lines[:5]:
        # name lines tend to be 2-4 words, mostly alphabetic, no @ or digits
        words = ln.split()
        if 2 <= len(words) <= 4 and all(re.match(r"^[a-z][a-z\.\-']*$", w) for w in words):
            return " ".join(w.capitalize() for w in words)
    # fallback: use filename stem
    return Path(fallback_filename).stem.replace("_", " ").replace("-", " ").title()


def _extract_email(text: str) -> str:
    m = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", text)
    return m.group(0) if m else ""


def _extract_phone(text: str) -> str:
    m = re.search(r"(\+?\d[\d\s\-]{8,}\d)", text)
    return m.group(1).strip() if m else ""


def _has_any(text: str, terms) -> bool:
    return any(t in text for t in terms)


def _kw_score(text: str, terms, points_each: int, cap: int) -> int:
    """Award `points_each` per matched term, capped at `cap`."""
    return min(sum(points_each for t in terms if t in text), cap)


def _score_core_tech(text: str, kw: dict, cap: int) -> int:
    s = _kw_score(text, kw["core_languages"], 5, 15)
    if _has_any(text, ["machine learning", "deep learning"]):
        s += 10
    if _has_any(text, ["nlp", "natural language processing"]):
        s += 5
    if _has_any(text, ["computer vision", "cv"]):
        s += 5
    if _has_any(text, ["sql", "mysql", "postgresql"]):
        s += 5
    if _has_any(text, ["nosql", "mongodb", "cassandra"]):
        s += 3
    if _has_any(text, ["artificial intelligence", "ai"]):
        s += 5
    return min(s, cap)


def _score_ml_de_tools(text: str, kw: dict, cap: int) -> int:
    s = _kw_score(text, kw["ml_frameworks"], 4, 12)
    s += _kw_score(text, kw["data_tools"], 3, 9)
    s += _kw_score(text, kw["viz_tools"], 2, 5)
    return min(s, cap)


def _score_cloud_mlops(text: str, kw: dict, cap: int) -> int:
    s = _kw_score(text, kw["cloud_platforms"], 4, 8)
    s += _kw_score(text, kw["mlops_tools"], 3, 9)
    return min(s, cap)


def _score_education(text: str, kw: dict, cap: int) -> int:
    s = 0
    if _has_any(text, kw["tier1_institutes"]):
        s += 10
    elif _has_any(text, ["university", "college"]):
        s += 5
    if _has_any(text, ["phd", "doctorate"]):
        s += 5
    elif _has_any(text, ["master", "m.tech", "m.sc", "mba"]):
        s += 3
    elif _has_any(text, ["bachelor", "b.tech", "b.sc", "b.e"]):
        s += 1
    return min(s, cap)


def _score_experience(text: str, kw: dict, cap: int) -> int:
    s = 0
    years = re.findall(r"(\d+)\s*\+?\s*year", text)
    if years:
        my = max(int(y) for y in years)
        s += 15 if my >= 5 else 10 if my >= 3 else 5 if my >= 1 else 0
    months = re.findall(r"(\d+)\s*month", text)
    if months and not years:
        s += 3
    if _has_any(text, kw["senior_roles"]):
        s += 5
    if _has_any(text, ["intern", "internship"]):
        s += 5
    return min(s, cap)


def _score_projects(text: str, cap: int) -> int:
    s = 0
    if _has_any(text, ["github", "gitlab", "bitbucket"]):
        s += 5
    if _has_any(text, ["open source", "contributor"]):
        s += 5
    if _has_any(text, ["portfolio", "project"]):
        s += 3
    if "kaggle" in text:
        s += 4
    return min(s, cap)


def _score_certs_research(text: str, kw: dict, cap: int) -> int:
    s = _kw_score(text, kw["recognized_certs"], 4, 8)
    if _has_any(text, ["certification", "certified"]):
        s += 2
    if _has_any(text, ["publication", "research paper", "arxiv", "ieee", "journal"]):
        s += 5
    return min(s, cap)


def _score_leadership(text: str, kw: dict, cap: int) -> int:
    return _kw_score(text, kw["leadership_kw"], 2, cap)


def _calc_penalty(text: str) -> int:
    pen = 0
    short_tenure = re.findall(r"(\d+)\s*month", text)
    if len(short_tenure) >= 4:
        pen += 5
    if _has_any(text, ["gap", "career break", "sabbatical"]):
        pen += 3
    return pen


def calculate_breakdown(text: str, settings: dict) -> dict:
    """Compute scoring breakdown using settings (weights + keyword lists)."""
    kw = settings["keywords"]
    w = settings["weights"]
    breakdown = {
        "core_tech": _score_core_tech(text, kw, w["core_tech"]),
        "ml_de_tools": _score_ml_de_tools(text, kw, w["ml_de_tools"]),
        "cloud_mlops": _score_cloud_mlops(text, kw, w["cloud_mlops"]),
        "education": _score_education(text, kw, w["education"]),
        "experience": _score_experience(text, kw, w["experience"]),
        "projects_opensource": _score_projects(text, w["projects_opensource"]),
        "certs_research": _score_certs_research(text, kw, w["certs_research"]),
        "leadership_soft": _score_leadership(text, kw, w["leadership_soft"]),
        "penalty": -_calc_penalty(text),
    }
    breakdown["total"] = max(sum(breakdown.values()), 0)
    return breakdown


def determine_status(score: int, thresholds: dict) -> str:
    if score >= thresholds["fast_track"]:
        return "Fast Track"
    elif score >= thresholds["shortlist"]:
        return "Shortlist"
    elif score >= thresholds["review"]:
        return "Review"
    else:
        return "Rejected"


def score_resume(file_bytes: bytes, filename: str, settings: dict) -> dict:
    """End-to-end: OCR + score + metadata extraction."""
    text = extract_text(file_bytes, filename)
    breakdown = calculate_breakdown(text, settings)
    status = determine_status(breakdown["total"], settings["thresholds"])
    return {
        "extracted_text": text,
        "name": _extract_candidate_name(text, filename),
        "email": _extract_email(text),
        "phone": _extract_phone(text),
        "breakdown": breakdown,
        "final_score": breakdown["total"],
        "status": status,
    }
