"""
FastAPI REST API Server for Ecg Qtc Calculator.
"""
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from qtc import calculate_qtc
from .base import AuditLogger, PHIGuard
from .models import SystemTaskPayload, ConsensusDossier
from .supervisor import SystemSupervisor

supervisor = SystemSupervisor(model_provider="mock")

app = FastAPI(
    title="Ecg Qtc Calculator API",
    description="ECG QTc calculation API and experimental legacy audit endpoints",
    version="3.0.0-ENTERPRISE",
)


class QTcRequest(BaseModel):
    qt_ms: float
    rr_ms: float | None = None
    hr_bpm: float | None = None
    sex: str = "male"


@app.post("/api/qtc")
def api_qtc(payload: QTcRequest):
    try:
        return calculate_qtc(payload.qt_ms, payload.rr_ms, payload.hr_bpm, payload.sex)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


class ChatRequest(BaseModel):
    query: str


@app.get("/health")
def health():
    return {"status": "HEALTHY", "service": "ecg-qtc-calculator", "domain": "Cardiology & Intensive Care Systems", "standard": "AHA/ACC Guidelines / Surviving Sepsis Campaign", "version": "3.0.0-ENTERPRISE"}


@app.get("/metrics")
def metrics():
    return {
        "dossiers_processed_total": len(supervisor.dossier_registry),
        "audit_blocks_total": len(AuditLogger.get_trail()),
        "system_status": "NOMINAL_OPTIMAL"
    }


@app.post("/api/audit")
def api_audit(payload: SystemTaskPayload):
    dossier = supervisor.process_task(payload)
    return dossier.to_dict()


@app.post("/api/chat")
def api_chat(req: ChatRequest):
    try:
        ans = supervisor.query_supervisory_chat(req.query)
        return {"response": ans}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/audit/logs")
def api_audit_logs():
    return {"audit_trail": AuditLogger.get_trail(), "verified": AuditLogger.verify_integrity()}
