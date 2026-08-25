#!/usr/bin/env python3
"""
ECG QTc Calculator
==================

Corrected QT interval (QTc) calculation using four standard formulas:

  - Bazett (1920):      QTc = QT / sqrt(RR)        [most common; overcorrects at high HR]
  - Fridericia (1920):  QTc = QT / (RR)^(1/3)      [better at extremes of HR]
  - Framingham (1992):  QTc = QT + 0.154*(1 - RR)  [linear regression model]
  - Hodges (1983):      QTc = QT + 1.75*(HR - 60)  [rate-corrected, no RR needed]

All inputs in milliseconds (ms).  RR interval can be derived from heart rate:
    RR (ms) = 60000 / HR (bpm)

Clinical thresholds (AHA/ACC):
    Normal:     QTc < 440 ms (male), < 460 ms (female)
    Prolonged:  QTc > 450 ms (male), > 470 ms (female)
    Dangerous:  QTc > 500 ms (high risk of Torsades de Pointes)

Stdlib only — no external dependencies.
"""

import math

# ── Clinical thresholds ──────────────────────────────────────────────

NORMAL_MALE_MS = 440
NORMAL_FEMALE_MS = 460
PROLONGED_MALE_MS = 450
PROLONGED_FEMALE_MS = 470
DANGEROUS_MS = 500


# ── Core calculations ────────────────────────────────────────────────

def rr_from_hr(hr_bpm):
    """Convert heart rate (bpm) to RR interval (ms).

    >>> rr_from_hr(60)
    1000.0
    >>> rr_from_hr(75)
    800.0
    """
    if hr_bpm <= 0:
        raise ValueError(f"Heart rate must be positive, got {hr_bpm}")
    return 60000.0 / hr_bpm


def hr_from_rr(rr_ms):
    """Convert RR interval (ms) to heart rate (bpm).

    >>> hr_from_rr(1000)
    60.0
    """
    if rr_ms <= 0:
        raise ValueError(f"RR interval must be positive, got {rr_ms}")
    return 60000.0 / rr_ms


def qtc_bazett(qt_ms, rr_ms):
    """Bazett formula: QTc = QT / sqrt(RR in seconds).

    Reference: Bazett HC. Heart 1920;7:353-370.
    Overcorrects at high heart rates, undercorrects at low heart rates.
    """
    if qt_ms <= 0:
        raise ValueError(f"QT must be positive, got {qt_ms}")
    if rr_ms <= 0:
        raise ValueError(f"RR must be positive, got {rr_ms}")
    rr_s = rr_ms / 1000.0
    return qt_ms / math.sqrt(rr_s)


def qtc_fridericia(qt_ms, rr_ms):
    """Fridericia formula: QTc = QT / (RR in seconds)^(1/3).

    Reference: Fridericia LS. Acta Med Scand 1920;53:469-486.
    Better performance at extreme heart rates than Bazett.
    """
    if qt_ms <= 0:
        raise ValueError(f"QT must be positive, got {qt_ms}")
    if rr_ms <= 0:
        raise ValueError(f"RR must be positive, got {rr_ms}")
    rr_s = rr_ms / 1000.0
    return qt_ms / (rr_s ** (1.0 / 3.0))


def qtc_framingham(qt_ms, rr_ms):
    """Framingham (Sagie) formula: QTc = QT + 0.154 * (1 - RR in seconds).

    Reference: Sagie A, et al. Am J Cardiol 1992;70:797-801.
    Linear regression correction from the Framingham Heart Study.
    """
    if qt_ms <= 0:
        raise ValueError(f"QT must be positive, got {qt_ms}")
    if rr_ms <= 0:
        raise ValueError(f"RR must be positive, got {rr_ms}")
    rr_s = rr_ms / 1000.0
    return qt_ms + 0.154 * (1.0 - rr_s)


def qtc_hodges(qt_ms, hr_bpm):
    """Hodges formula: QTc = QT + 1.75 * (HR - 60).

    Reference: Hodges M, et al. Am J Cardiol 1983;51:1577-1578.
    Does not require RR interval; uses heart rate directly.
    """
    if qt_ms <= 0:
        raise ValueError(f"QT must be positive, got {qt_ms}")
    if hr_bpm <= 0:
        raise ValueError(f"Heart rate must be positive, got {hr_bpm}")
    return qt_ms + 1.75 * (hr_bpm - 60.0)


# ── QT dispersion ────────────────────────────────────────────────────

def qt_dispersion(qt_max_ms, qt_min_ms):
    """QT dispersion = max QT - min QT across the 12-lead ECG.

    Normal: < 40 ms.  Increased dispersion suggests heterogeneous
    ventricular repolarization and increased arrhythmia risk.

    Reference: Day CP, et al. BMJ 1990;300:671-673.
    """
    if qt_max_ms < 0 or qt_min_ms < 0:
        raise ValueError("QT values must be non-negative")
    if qt_min_ms > qt_max_ms:
        raise ValueError("QT min cannot exceed QT max")
    return qt_max_ms - qt_min_ms


# ── Comprehensive assessment ─────────────────────────────────────────

def classify_qtc(qtc_ms, sex="male"):
    """Classify a QTc value by clinical thresholds.

    Returns one of: 'normal', 'borderline', 'prolonged', 'dangerous'.

    Thresholds per AHA/ACC 2010 guidelines:
        Male:   normal < 440, borderline 440-450, prolonged > 450
        Female: normal < 460, borderline 460-470, prolonged > 470
        Both:   dangerous > 500 (Torsades de Pointes risk)
    """
    sex = sex.lower()
    if qtc_ms >= DANGEROUS_MS:
        return "dangerous"
    if sex in ("male", "m"):
        if qtc_ms < NORMAL_MALE_MS:
            return "normal"
        elif qtc_ms <= PROLONGED_MALE_MS:
            return "borderline"
        else:
            return "prolonged"
    elif sex in ("female", "f"):
        if qtc_ms < NORMAL_FEMALE_MS:
            return "normal"
        elif qtc_ms <= PROLONGED_FEMALE_MS:
            return "borderline"
        else:
            return "prolonged"
    else:
        raise ValueError(f"Unknown sex '{sex}'; use 'male' or 'female'")


def calculate_qtc(qt_ms, rr_ms=None, hr_bpm=None, sex="male"):
    """Calculate QTc by all four formulas and return a full assessment.

    Provide either rr_ms (RR interval in ms) or hr_bpm (heart rate in bpm).
    If both are given, rr_ms takes precedence.

    Returns a dict with all four QTc values, classification, and metadata.
    """
    if rr_ms is None and hr_bpm is None:
        raise ValueError("Must provide either rr_ms or hr_bpm")
    if qt_ms <= 0:
        raise ValueError(f"QT must be positive, got {qt_ms}")

    # Derive RR from HR if needed
    if rr_ms is None:
        rr_ms = rr_from_hr(hr_bpm)
    if rr_ms <= 0:
        raise ValueError(f"RR interval must be positive, got {rr_ms}")

    # Derive HR from RR
    hr = hr_from_rr(rr_ms)

    # Calculate all four
    baz = qtc_bazett(qt_ms, rr_ms)
    fri = qtc_fridericia(qt_ms, rr_ms)
    fra = qtc_framingham(qt_ms, rr_ms)
    hod = qtc_hodges(qt_ms, hr)

    # Classify by Bazett (most commonly used clinically)
    flag = classify_qtc(baz, sex)

    return {
        "qt_ms": round(qt_ms, 1),
        "rr_ms": round(rr_ms, 1),
        "hr_bpm": round(hr, 1),
        "sex": sex,
        "qtc_bazett": round(baz, 1),
        "qtc_fridericia": round(fri, 1),
        "qtc_framingham": round(fra, 1),
        "qtc_hodges": round(hod, 1),
        "classification": flag,
    }


# ── CSV batch processing ─────────────────────────────────────────────

def process_csv(input_path, output_path):
    """Process a CSV file of QT measurements and write QTc results.

    Expected columns: qt_ms (or qt), and one of: rr_ms, hr_bpm (or heart_rate).
    Optional column: sex (default 'male').
    """
    import csv

    with open(input_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames or [])
        rows = list(reader)

    results = []
    for row in rows:
        try:
            qt = float(row.get("qt_ms") or row.get("qt"))
            rr = row.get("rr_ms")
            hr = row.get("hr_bpm") or row.get("heart_rate")
            sex = row.get("sex", "male")
            res = calculate_qtc(
                qt,
                rr_ms=float(rr) if rr else None,
                hr_bpm=float(hr) if hr else None,
                sex=sex,
            )
        except (ValueError, TypeError, KeyError) as e:
            res = {"error": str(e)}
        merged = {**row, **{k: str(v) for k, v in res.items()}}
        results.append(merged)

    # Build output fieldnames
    all_keys = set()
    for r in results:
        all_keys.update(r.keys())
    extra = sorted(k for k in all_keys if k not in fieldnames)
    out_fields = fieldnames + extra

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=out_fields)
        writer.writeheader()
        writer.writerows(results)

    return results
