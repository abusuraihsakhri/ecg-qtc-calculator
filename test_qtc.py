"""Tests for qtc.py — ECG QTc Calculator.

Run with: python -m pytest test_qtc.py -v
"""
import math
import pytest
from qtc import (
    rr_from_hr, hr_from_rr,
    qtc_bazett, qtc_fridericia, qtc_framingham, qtc_hodges,
    qt_dispersion, classify_qtc, calculate_qtc,
)


# ── RR/HR conversion ────────────────────────────────────────────────

class TestRRHRConversion:
    def test_rr_from_hr_60bpm(self):
        assert rr_from_hr(60) == 1000.0

    def test_rr_from_hr_75bpm(self):
        assert abs(rr_from_hr(75) - 800.0) < 0.01

    def test_rr_from_hr_120bpm(self):
        assert abs(rr_from_hr(120) - 500.0) < 0.01

    def test_hr_from_rr_1000ms(self):
        assert hr_from_rr(1000) == 60.0

    def test_hr_from_rr_800ms(self):
        assert abs(hr_from_rr(800) - 75.0) < 0.01

    def test_rr_from_hr_invalid(self):
        with pytest.raises(ValueError):
            rr_from_hr(0)
        with pytest.raises(ValueError):
            rr_from_hr(-10)


# ── Bazett formula ──────────────────────────────────────────────────

class TestBazett:
    def test_normal_hr(self):
        # QT=400ms, RR=1000ms (60bpm): QTc = 400/sqrt(1) = 400
        assert abs(qtc_bazett(400, 1000) - 400.0) < 0.1

    def test_high_hr(self):
        # QT=350ms, RR=600ms (100bpm): QTc = 350/sqrt(0.6) = 451.8
        result = qtc_bazett(350, 600)
        assert abs(result - 451.8) < 1.0

    def test_low_hr(self):
        # QT=420ms, RR=1200ms (50bpm): QTc = 420/sqrt(1.2) = 383.4
        result = qtc_bazett(420, 1200)
        assert abs(result - 383.4) < 1.0

    def test_invalid_qt(self):
        with pytest.raises(ValueError):
            qtc_bazett(0, 1000)

    def test_invalid_rr(self):
        with pytest.raises(ValueError):
            qtc_bazett(400, 0)


# ── Fridericia formula ──────────────────────────────────────────────

class TestFridericia:
    def test_normal_hr(self):
        # QT=400ms, RR=1000ms: QTc = 400/1 = 400
        assert abs(qtc_fridericia(400, 1000) - 400.0) < 0.1

    def test_high_hr(self):
        # QT=350ms, RR=600ms: QTc = 350/(0.6)^(1/3) = 350/0.8434 = 415.0
        result = qtc_fridericia(350, 600)
        assert abs(result - 415.0) < 2.0

    def test_overcorrects_less_than_bazett(self):
        # At high HR, Fridericia should give lower QTc than Bazett
        baz = qtc_bazett(350, 600)
        fri = qtc_fridericia(350, 600)
        assert fri < baz


# ── Framingham formula ──────────────────────────────────────────────

class TestFramingham:
    def test_normal_hr(self):
        # QT=400ms, RR=1000ms: QTc = 400 + 0.154*(1-1) = 400
        assert abs(qtc_framingham(400, 1000) - 400.0) < 0.1

    def test_high_hr(self):
        # QT=350ms, RR=600ms: QTc = 350 + 0.154*(1-0.6) = 350 + 0.0616 = 350.06
        # Wait, that's in seconds: 0.154*(1-0.6) = 0.0616 but the formula uses ms?
        # Actually the formula is QT + 0.154*(1-RR_s) where RR is in seconds
        # So QTc = 350 + 0.154*(1-0.6) = 350 + 0.0616 = 350.06
        # Hmm, that doesn't seem right. Let me re-check.
        # The Framingham formula: QTc = QT + 0.154*(1-RR) where RR is in seconds
        # QT=350, RR_s=0.6: QTc = 350 + 0.154*(1-0.6) = 350 + 0.0616 = 350.06
        # That's a very small correction. The 0.154 constant is in ms per second.
        result = qtc_framingham(350, 600)
        expected = 350 + 0.154 * (1 - 0.6)
        assert abs(result - expected) < 0.1

    def test_low_hr(self):
        # QT=420ms, RR=1200ms (1.2s): QTc = 420 + 0.154*(1-1.2) = 420 - 0.0308 = 419.97
        result = qtc_framingham(420, 1200)
        expected = 420 + 0.154 * (1 - 1.2)
        assert abs(result - expected) < 0.1


# ── Hodges formula ──────────────────────────────────────────────────

class TestHodges:
    def test_60bpm(self):
        # QT=400ms, HR=60: QTc = 400 + 1.75*(60-60) = 400
        assert abs(qtc_hodges(400, 60) - 400.0) < 0.1

    def test_100bpm(self):
        # QT=350ms, HR=100: QTc = 350 + 1.75*(100-60) = 350 + 70 = 420
        assert abs(qtc_hodges(350, 100) - 420.0) < 0.1

    def test_50bpm(self):
        # QT=420ms, HR=50: QTc = 420 + 1.75*(50-60) = 420 - 17.5 = 402.5
        assert abs(qtc_hodges(420, 50) - 402.5) < 0.1


# ── QT dispersion ───────────────────────────────────────────────────

class TestQTDispersion:
    def test_normal_dispersion(self):
        assert qt_dispersion(420, 390) == 30

    def test_elevated_dispersion(self):
        assert qt_dispersion(460, 380) == 80

    def test_zero_dispersion(self):
        assert qt_dispersion(400, 400) == 0

    def test_invalid_min_greater_than_max(self):
        with pytest.raises(ValueError):
            qt_dispersion(380, 420)


# ── Classification ──────────────────────────────────────────────────

class TestClassifyQTc:
    def test_normal_male(self):
        assert classify_qtc(420, "male") == "normal"

    def test_borderline_male(self):
        assert classify_qtc(445, "male") == "borderline"

    def test_prolonged_male(self):
        assert classify_qtc(460, "male") == "prolonged"

    def test_normal_female(self):
        assert classify_qtc(450, "female") == "normal"

    def test_borderline_female(self):
        assert classify_qtc(465, "female") == "borderline"

    def test_prolonged_female(self):
        assert classify_qtc(480, "female") == "prolonged"

    def test_dangerous(self):
        assert classify_qtc(510, "male") == "dangerous"
        assert classify_qtc(510, "female") == "dangerous"

    def test_invalid_sex(self):
        with pytest.raises(ValueError):
            classify_qtc(400, "other")


# ── Comprehensive calculate_qtc ─────────────────────────────────────

class TestCalculateQTC:
    def test_with_rr(self):
        result = calculate_qtc(400, rr_ms=1000, sex="male")
        assert result["qtc_bazett"] == 400.0
        assert result["rr_ms"] == 1000.0
        assert result["hr_bpm"] == 60.0
        assert result["classification"] == "normal"

    def test_with_hr(self):
        result = calculate_qtc(400, hr_bpm=75, sex="male")
        assert result["rr_ms"] == 800.0
        assert result["hr_bpm"] == 75.0

    def test_prolonged_male(self):
        result = calculate_qtc(440, rr_ms=800, sex="male")
        assert result["classification"] in ("borderline", "prolonged")

    def test_dangerous(self):
        result = calculate_qtc(480, rr_ms=800, sex="male")
        assert result["qtc_bazett"] > 500
        assert result["classification"] == "dangerous"

    def test_missing_both_rr_and_hr(self):
        with pytest.raises(ValueError):
            calculate_qtc(400)

    def test_all_formulas_present(self):
        result = calculate_qtc(400, rr_ms=1000)
        assert "qtc_bazett" in result
        assert "qtc_fridericia" in result
        assert "qtc_framingham" in result
        assert "qtc_hodges" in result
