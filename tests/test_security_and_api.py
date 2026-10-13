"""Validate QTc API calculations and audit chain tamper detection."""
import pytest
from fastapi import HTTPException
from agents.api import QTcRequest, api_qtc
from agents.base import AuditTrail

def test_api_calculates_all_four_formulas():
    result=api_qtc(QTcRequest(qt_ms=350, rr_ms=600, sex="male"))
    assert result["qtc_framingham"] == 411.6
    assert result["qtc_hodges"] == 420.0

def test_api_rejects_invalid_measurements():
    with pytest.raises(HTTPException) as exc:
        api_qtc(QTcRequest(qt_ms=0, rr_ms=600))
    assert exc.value.status_code == 422

def test_audit_integrity_detects_entry_change():
    trail=AuditTrail(secret_key="test-only-key")
    entry=trail.log("unit","test","event",{"result":"ok"})
    assert trail.verify_integrity()
    entry["event_type"]="modified"
    assert not trail.verify_integrity()

def test_audit_integrity_detects_signature_change():
    trail=AuditTrail(secret_key="test-only-key")
    trail.log("unit","test","event",{"result":"ok"})
    assert trail.verify_integrity()
    trail.logs[0]["current_hash"]="0"*64
    assert not trail.verify_integrity()
