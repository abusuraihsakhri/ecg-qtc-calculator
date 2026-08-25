# ECG QTc Calculator

Corrected QT interval (QTc) calculation using four standard clinical formulas.

## Formulas Implemented

| Formula | Equation | Notes |
|---------|----------|-------|
| **Bazett** (1920) | `QTc = QT / √RR` | Most common; overcorrects at high HR |
| **Fridericia** (1920) | `QTc = QT / RR^(1/3)` | Better at extreme heart rates |
| **Framingham** (1992) | `QTc = QT + 0.154 × (1 - RR)` | Linear regression from Framingham Heart Study |
| **Hodges** (1983) | `QTc = QT + 1.75 × (HR - 60)` | Rate-corrected, no RR interval needed |

All inputs in milliseconds (ms). RR interval can be derived from heart rate: `RR = 60000 / HR`.

## Clinical Thresholds

| Category | Male | Female |
|----------|------|--------|
| Normal | QTc < 440 ms | QTc < 460 ms |
| Borderline | 440-450 ms | 460-470 ms |
| Prolonged | QTc > 450 ms | QTc > 470 ms |
| Dangerous | QTc > 500 ms (Torsades de Pointes risk) | QTc > 500 ms |

## Quick Start

```bash
# Single calculation (from RR interval)
python cli.py single --qt 400 --rr 800

# Single calculation (from heart rate)
python cli.py single --qt 400 --hr 75 --sex female

# QT dispersion
python cli.py dispersion --qt-max 440 --qt-min 380

# Batch CSV processing
python cli.py batch -i sample.csv -o results.csv
```

## Python API

```python
from qtc import calculate_qtc, qtc_bazett, classify_qtc, qt_dispersion

# Full assessment
result = calculate_qtc(qt_ms=400, rr_ms=800, sex="male")
print(result)
# {'qt_ms': 400.0, 'rr_ms': 800.0, 'hr_bpm': 75.0, 'sex': 'male',
#  'qtc_bazett': 447.2, 'qtc_fridericia': 430.9, ...}

# Individual formula
bazett = qtc_bazett(qt_ms=400, rr_ms=800)  # 447.2

# Classification
classify_qtc(460, sex="male")  # "prolonged"

# QT dispersion
qt_dispersion(qt_max_ms=440, qt_min_ms=380)  # 60 ms (elevated)
```

## Dependencies

Python standard library only. No external packages required.

## License

MIT License.
