"""SignalRank backend API tests."""
import io
import os
import csv
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://exec-ui.preview.emergentagent.com").rstrip("/")
API = f"{BASE_URL}/api"


# --- Health ---
def test_root_status():
    r = requests.get(f"{API}/")
    assert r.status_code == 200
    data = r.json()
    assert data["service"] == "SignalRank"
    assert data["status"] == "ok"


def test_categories():
    r = requests.get(f"{API}/categories")
    assert r.status_code == 200
    data = r.json()
    expected_keys = {
        "core_tech", "ml_de_tools", "cloud_mlops", "education",
        "experience", "projects_opensource", "certs_research", "leadership_soft",
    }
    assert expected_keys.issubset(set(data.keys()))


# --- Settings ---
class TestSettings:
    def test_get_settings(self):
        r = requests.get(f"{API}/settings")
        assert r.status_code == 200
        data = r.json()
        assert "weights" in data and "keywords" in data and "thresholds" in data
        assert data["weights"]["core_tech"] >= 0
        assert "fast_track" in data["thresholds"]

    def test_put_and_reset_settings(self):
        # Capture defaults
        original = requests.get(f"{API}/settings").json()
        modified = {
            "weights": {**original["weights"], "core_tech": original["weights"]["core_tech"] + 5},
            "keywords": original["keywords"],
            "thresholds": {**original["thresholds"], "fast_track": 80},
        }
        r = requests.put(f"{API}/settings", json=modified)
        assert r.status_code == 200, r.text
        assert r.json()["weights"]["core_tech"] == original["weights"]["core_tech"] + 5

        verify = requests.get(f"{API}/settings").json()
        assert verify["thresholds"]["fast_track"] == 80

        # Reset
        r2 = requests.post(f"{API}/settings/reset")
        assert r2.status_code == 200
        reset_data = r2.json()
        assert reset_data["thresholds"]["fast_track"] == 75
        assert reset_data["weights"]["core_tech"] == 30


# --- Resumes / Stats / Listing ---
class TestResumes:
    def test_stats(self):
        r = requests.get(f"{API}/resumes/stats")
        assert r.status_code == 200
        data = r.json()
        for k in ("total", "avg_score", "fast_track", "shortlist", "review", "rejected"):
            assert k in data
        assert isinstance(data["total"], int)

    def test_list_sorted_desc(self):
        r = requests.get(f"{API}/resumes")
        assert r.status_code == 200
        items = r.json()
        assert isinstance(items, list)
        if len(items) > 1:
            scores = [i["final_score"] for i in items]
            assert scores == sorted(scores, reverse=True), "List should be sorted by final_score desc"
        # Each item should not leak _id
        for it in items:
            assert "_id" not in it
            assert "id" in it
            assert "breakdown" in it

    def test_status_filter(self):
        r = requests.get(f"{API}/resumes", params={"status": "Fast Track"})
        assert r.status_code == 200
        for it in r.json():
            assert it["status"] == "Fast Track"

    def test_search_query(self):
        # use empty common letter to search; ensure no 500
        r = requests.get(f"{API}/resumes", params={"q": "a"})
        assert r.status_code == 200
        assert isinstance(r.json(), list)


# --- Upload + per-candidate ops ---
class TestUploadAndCandidate:
    @pytest.fixture(scope="class")
    def uploaded_candidate(self):
        # Create a synthetic resume PNG via PIL
        try:
            from PIL import Image, ImageDraw
        except ImportError:
            pytest.skip("PIL not available")

        img = Image.new("RGB", (1200, 1600), "white")
        d = ImageDraw.Draw(img)
        resume_text = [
            "TEST Candidate",
            "test_candidate@example.com  +1 555 123 4567",
            "",
            "Senior Machine Learning Engineer with 7+ years experience",
            "Skills: Python, Java, TensorFlow, PyTorch, scikit-learn",
            "Cloud: AWS, GCP, Docker, Kubernetes, MLflow",
            "Data: Spark, Kafka, Airflow, SQL, PostgreSQL",
            "Education: MIT - Master of Science in Computer Science",
            "Experience: Led a team of 5, mentored junior engineers",
            "Projects: GitHub portfolio, open source contributor, Kaggle",
            "Certifications: AWS Certified Solutions Architect, Coursera",
            "Research: IEEE publication on deep learning",
        ]
        y = 50
        for line in resume_text:
            d.text((50, y), line, fill="black")
            y += 60
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)

        files = [("files", ("TEST_resume.png", buf.getvalue(), "image/png"))]
        r = requests.post(f"{API}/resumes/upload", files=files)
        assert r.status_code == 200, r.text
        data = r.json()
        assert "processed" in data and "errors" in data
        assert len(data["processed"]) == 1, f"Expected 1 processed, got: {data}"
        candidate = data["processed"][0]
        assert "id" in candidate and "final_score" in candidate and "status" in candidate
        yield candidate
        # cleanup
        requests.delete(f"{API}/resumes/{candidate['id']}")

    def test_upload_unsupported_type(self):
        files = [("files", ("badfile.txt", b"hello world", "text/plain"))]
        r = requests.post(f"{API}/resumes/upload", files=files)
        assert r.status_code == 200
        data = r.json()
        assert len(data["errors"]) == 1
        assert "Unsupported" in data["errors"][0]["error"]
        assert len(data["processed"]) == 0

    def test_upload_mixed_files(self):
        try:
            from PIL import Image
        except ImportError:
            pytest.skip("PIL not available")
        img = Image.new("RGB", (200, 200), "white")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        files = [
            ("files", ("TEST_mixed.png", buf.getvalue(), "image/png")),
            ("files", ("TEST_bad.exe", b"binary", "application/octet-stream")),
        ]
        r = requests.post(f"{API}/resumes/upload", files=files)
        assert r.status_code == 200
        data = r.json()
        assert len(data["processed"]) == 1
        assert len(data["errors"]) == 1
        # cleanup
        if data["processed"]:
            requests.delete(f"{API}/resumes/{data['processed'][0]['id']}")

    def test_get_candidate_detail(self, uploaded_candidate):
        cid = uploaded_candidate["id"]
        r = requests.get(f"{API}/resumes/{cid}")
        assert r.status_code == 200
        data = r.json()
        assert data["id"] == cid
        assert "breakdown" in data
        assert "extracted_text" in data
        for k in ("core_tech", "ml_de_tools", "cloud_mlops", "education",
                  "experience", "projects_opensource", "certs_research",
                  "leadership_soft", "total"):
            assert k in data["breakdown"]
        # status bucketing sanity
        assert data["status"] in ("Fast Track", "Shortlist", "Review", "Rejected")

    def test_get_candidate_404(self):
        r = requests.get(f"{API}/resumes/nonexistent-id-xyz")
        assert r.status_code == 404

    def test_decision_update(self, uploaded_candidate):
        cid = uploaded_candidate["id"]
        r = requests.patch(f"{API}/resumes/{cid}/decision", json={"decision": "selected"})
        assert r.status_code == 200
        assert r.json()["decision"] == "selected"

        # Update to hold
        r = requests.patch(f"{API}/resumes/{cid}/decision", json={"decision": "hold"})
        assert r.status_code == 200
        assert r.json()["decision"] == "hold"

        # Clear decision
        r = requests.patch(f"{API}/resumes/{cid}/decision", json={"decision": ""})
        assert r.status_code == 200
        assert r.json()["decision"] == ""

    def test_decision_404(self):
        r = requests.patch(f"{API}/resumes/missing-id/decision", json={"decision": "selected"})
        assert r.status_code == 404


# --- Export ---
def test_export_csv():
    r = requests.get(f"{API}/resumes/export")
    assert r.status_code == 200
    assert "text/csv" in r.headers.get("content-type", "")
    text = r.text
    rows = list(csv.reader(io.StringIO(text)))
    assert len(rows) >= 1
    header = rows[0]
    for col in ("rank", "name", "email", "phone", "filename", "status", "final_score",
                "core_tech", "ml_de_tools", "cloud_mlops", "education",
                "experience", "projects_opensource", "certs_research",
                "leadership_soft", "penalty"):
        assert col in header, f"Missing CSV column: {col}"
    # Each data row's status should be Fast Track or Shortlist
    for row in rows[1:]:
        status_idx = header.index("status")
        assert row[status_idx] in ("Fast Track", "Shortlist")


# --- Rescore ---
def test_rescore_all():
    r = requests.post(f"{API}/resumes/rescore")
    assert r.status_code == 200
    data = r.json()
    assert "updated" in data
    assert isinstance(data["updated"], int)


# --- Threshold bucketing sanity ---
def test_status_thresholds_consistent():
    """Verify candidate statuses match current thresholds."""
    settings = requests.get(f"{API}/settings").json()
    t = settings["thresholds"]
    candidates = requests.get(f"{API}/resumes").json()
    for c in candidates:
        s = c["final_score"]
        if s >= t["fast_track"]:
            expected = "Fast Track"
        elif s >= t["shortlist"]:
            expected = "Shortlist"
        elif s >= t["review"]:
            expected = "Review"
        else:
            expected = "Rejected"
        assert c["status"] == expected, f"Candidate {c['id']} score={s} status={c['status']} expected={expected}"


# --- Delete flow ---
def test_delete_candidate_flow():
    try:
        from PIL import Image
    except ImportError:
        pytest.skip("PIL not available")
    img = Image.new("RGB", (200, 200), "white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    files = [("files", ("TEST_delete_me.png", buf.getvalue(), "image/png"))]
    r = requests.post(f"{API}/resumes/upload", files=files)
    assert r.status_code == 200
    cid = r.json()["processed"][0]["id"]

    rd = requests.delete(f"{API}/resumes/{cid}")
    assert rd.status_code == 200
    assert rd.json()["deleted"] == cid

    rget = requests.get(f"{API}/resumes/{cid}")
    assert rget.status_code == 404


def test_delete_404():
    r = requests.delete(f"{API}/resumes/missing-id-zzz")
    assert r.status_code == 404
