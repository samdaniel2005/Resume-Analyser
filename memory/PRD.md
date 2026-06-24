# SignalRank — Resume Intelligence Platform

## Original Problem Statement
> "give me professional ui for my project"

User uploaded `main.py`: a Python script doing OCR-based resume screening with weighted heuristic scoring across 8 categories.

## User Choices Captured
- Full web app (React + FastAPI)
- All flows: drag-drop multi-upload, ranked dashboard, candidate detail, editable weights & keywords, CSV export
- Generic branding (renamed "SignalRank")
- Modern recruiter SaaS aesthetic (Greenhouse/Lever-style)
- Real OCR + scoring in backend (Tesseract + opencv + pdf2image)

## Architecture
- **Frontend**: React 19 + React Router, Tailwind, Cabinet Grotesk / Satoshi fonts (Fontshare), lucide-react icons, brand color #002FA7
- **Backend**: FastAPI + Motor (async Mongo), pytesseract, opencv-python-headless, pdf2image, Pillow
- **System deps**: tesseract-ocr 5.3, poppler-utils
- **Persistence**: MongoDB collections `candidates`, `settings` (single doc id="global"); uploaded files stored under `/app/backend/uploads/`

## Core Requirements (static)
- Score breakdown by 8 categories — exact logic from user's `main.py`
- Status buckets: Fast Track (≥75), Shortlist (≥55), Review (≥35), Rejected
- Editable weights, thresholds, keyword lists
- CSV export of shortlisted (Fast Track + Shortlist)
- Re-score all candidates whenever settings change

## Implemented (2026-01-24)
- Backend
  - GET /api/, /api/categories
  - GET/PUT /api/settings, POST /api/settings/reset
  - POST /api/resumes/upload (multipart, PDF + JPG/PNG/WEBP/TIFF/BMP)
  - GET /api/resumes (filter by status, search by q)
  - GET /api/resumes/stats
  - GET /api/resumes/export (CSV)
  - GET /api/resumes/{id}
  - PATCH /api/resumes/{id}/decision (selected/hold/rejected)
  - DELETE /api/resumes/{id}
  - POST /api/resumes/rescore (recompute all with current settings)
- Frontend
  - Sidebar layout with 4 nav items
  - `/` Dashboard: KPI cards + top candidates list + empty state
  - `/candidates` Ranked table with status filter, search, re-score, CSV export, full-row click navigation
  - `/upload` Drag-and-drop multi-file with queue, scoring progress, per-file result
  - `/candidates/:id` Composite score, status badge, 8-category breakdown bars, recruiter decision buttons, OCR extract preview, delete
  - `/settings` 3 tabs: Weights (sliders + numbers), Thresholds, Keyword chips (add/remove for 10 groups); save auto re-scores
- Testing
  - 19 pytest backend tests, 100% pass
  - Full UI Playwright coverage by testing agent, 100% pass
  - Pytest file: `/app/backend/tests/test_signalrank.py`

## Backlog / Future Ideas
- P1: Replace `window.confirm` with shadcn AlertDialog for design consistency
- P1: Tighten keyword matching with word boundaries (e.g., `\bai\b`, `\bcv\b`) to reduce false positives
- P1: Bulk select + bulk decision (select/reject) on Candidates page
- P2: Per-role scoring profiles (save & switch presets like "ML Engineer" vs "Frontend")
- P2: Resume preview (PDF.js) on detail page in addition to OCR text
- P2: Authentication (JWT or Emergent Google Auth) for multi-recruiter use
- P2: Email notifications for new top-scoring candidates
- P2: Score history / audit log when settings change

## Key Files
- `/app/backend/server.py` — FastAPI app + routes
- `/app/backend/scoring.py` — OCR + scoring engine adapted from user's main.py
- `/app/frontend/src/App.js` — routes
- `/app/frontend/src/components/AppLayout.jsx` — sidebar
- `/app/frontend/src/pages/{Dashboard,Candidates,UploadPage,CandidateDetail,Settings}.jsx`
- `/app/frontend/src/lib/api.js` — API client + constants
- `/app/design_guidelines.json` — design system spec
