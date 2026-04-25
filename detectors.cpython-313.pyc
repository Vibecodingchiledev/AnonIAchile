from __future__ import annotations

import hashlib
import json
import secrets
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from anonym_metric import compute_metric
from anonymize_improved import AllAnonym, LabelAnonym, RandomAnonym, anonymizeSpans
from app.detectors import detect_spans
from app.schemas import AnonymizeRequest
from meta import Span

BASE_DIR = Path(__file__).resolve().parent.parent
REPORTS_DIR = BASE_DIR / "reports"
REPORTS_DIR.mkdir(exist_ok=True)

app = FastAPI(title="Privacy Gateway CL", version="0.1.0")
app.mount("/static", StaticFiles(directory=BASE_DIR / "app" / "static"), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "app" / "templates"))

JOB_STORE: Dict[str, dict] = {}
DEMO_USERS = {
    "admin@demo.cl": {"password": "demo123", "role": "admin"},
    "auditor@demo.cl": {"password": "demo123", "role": "auditor"},
    "researcher@demo.cl": {"password": "demo123", "role": "researcher"},
}


@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "demo_users": DEMO_USERS,
            "jobs": list(JOB_STORE.values())[-10:][::-1],
        },
    )


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "service": "privacy-gateway-cl", "time": _utc_now()}


@app.post("/api/login")
def login(email: str = Form(...), password: str = Form(...)) -> dict:
    user = DEMO_USERS.get(email)
    if not user or user["password"] != password:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    token = secrets.token_urlsafe(24)
    return {"access_token": token, "token_type": "bearer", "role": user["role"], "email": email}


@app.post("/api/anonymize")
def anonymize(payload: AnonymizeRequest):
    return _run_job(payload.text, payload.method, payload.role, payload.responsible_user, payload.irreversible, payload.dataset_name)


@app.post("/api/anonymize-file")
async def anonymize_file(
    file: UploadFile = File(...),
    method: str = Form("intelligent"),
    role: str = Form("researcher"),
    responsible_user: str = Form("demo_user"),
):
    content = await file.read()
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise HTTPException(status_code=400, detail="Solo se admite UTF-8 en este MVP") from exc
    return _run_job(text, method, role, responsible_user, True, file.filename)


@app.get("/api/jobs")
def list_jobs() -> List[dict]:
    return list(JOB_STORE.values())[::-1]


@app.get("/api/jobs/{job_id}")
def get_job(job_id: str) -> dict:
    job = JOB_STORE.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job no encontrado")
    return job


@app.get("/api/jobs/{job_id}/report")
def get_report(job_id: str):
    path = REPORTS_DIR / f"{job_id}.json"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Reporte no encontrado")
    return JSONResponse(json.loads(path.read_text(encoding="utf-8")))



def _run_job(text: str, method: str, role: str, responsible_user: str, irreversible: bool, dataset_name: str | None) -> dict:
    if method not in {"intelligent", "label", "random"}:
        raise HTTPException(status_code=400, detail="Método inválido")
    if role not in {"admin", "auditor", "operator", "researcher", "api_client"}:
        raise HTTPException(status_code=400, detail="Rol inválido")

    spans = detect_spans(text)
    anonymizer = _pick_anonymizer(method)
    new_spans, new_text = anonymizeSpans(anonymizer, [s.copy() for s in spans], text)

    metric = compute_metric(spans, new_spans)
    job_id = secrets.token_hex(8)
    report = {
        "job_id": job_id,
        "dataset_name": dataset_name or "text-input",
        "responsible_user": responsible_user,
        "timestamp": _utc_now(),
        "original_hash": _sha256(text),
        "anonymized_hash": _sha512(new_text),
        "status": "Anonimización irreversible aplicada" if irreversible else "Seudonimización / máscara aplicada",
        "method": method,
        "role": role,
        "detected_spans": spans,
        "anonymized_spans": new_spans,
        "text": text,
        "anonymized_text": new_text,
        "risk_summary": {
            "entities_detected": metric["num_entities"],
            "entities_exactly_covered": metric["exact"],
            "chars_total_sensitive": metric["chars_total"],
            "chars_hidden": metric["chars_hidden"],
            "coverage_ratio": round(metric["chars_hidden"] / metric["chars_total"], 3) if metric["chars_total"] else 0,
        },
        "compliance_standards": ["Ley 19.628", "Ley 21.719", "ISO 27001", "ISO 27701"],
        "hsm_custody": {
            "custody": "SIMULADO - sustituir por HSM real en producción",
            "pqc_key": "SIMULATED-KYBER-PLACEHOLDER",
        },
    }
    JOB_STORE[job_id] = report
    (REPORTS_DIR / f"{job_id}.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report



def _pick_anonymizer(method: str):
    if method == "label":
        return LabelAnonym()
    if method == "random":
        return RandomAnonym()
    return AllAnonym()



def _sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()



def _sha512(value: str) -> str:
    return hashlib.sha512(value.encode("utf-8")).hexdigest()



def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()
