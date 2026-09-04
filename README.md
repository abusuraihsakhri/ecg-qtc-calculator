# ECG QTc Calculator

> **Domain:** Cardiovascular Medicine & Hemodynamic Analytics
> **Reference Guidelines & Standards:** AHA/ACC Practice Guidelines & ESC Clinical Standards

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)

</div>

---

## What It Does

ECG QTc Calculator computes the corrected QT interval (QTc) using four standard formulas:

- **Bazett (1920):** QTc = QT / sqrt(RR) — most common; overcorrects at high HR
- **Fridericia (1920):** QTc = QT / (RR)^(1/3) — better at extremes of HR
- **Framingham (1992):** QTc = QT + 0.154*(1 - RR) — linear regression model
- **Hodges (1983):** QTc = QT + 1.75*(HR - 60) — rate-corrected, no RR needed

All inputs in milliseconds (ms). RR interval can be derived from heart rate:
```
RR (ms) = 60000 / HR (bpm)
```

Clinical thresholds (AHA/ACC):
- **Normal:** QTc < 440 ms (male), < 460 ms (female)
- **Prolonged:** QTc > 450 ms (male), > 470 ms (female)
- **Dangerous:** QTc > 500 ms (high risk of Torsades de Pointes)

---

## Installation

```bash
git clone https://github.com/abusuraihsakhri/ecg-qtc-calculator.git
cd ecg-qtc-calculator
```

No external dependencies required for core functionality. The core module (`qtc.py`) uses only Python stdlib.

For the optional FastAPI server and enterprise features:
```bash
pip install fastapi uvicorn pydantic pytest
```

---

## Usage

### Command Line Interface

#### Single Patient Calculation
```bash
# Using RR interval
python cli.py single --qt 400 --rr 1000 --sex male

# Using heart rate
python cli.py single --qt 400 --hr 75 --sex female
```

#### QT Dispersion
```bash
python cli.py dispersion --qt-max 420 --qt-min 390
```

#### Batch CSV Processing
```bash
python cli.py batch -i sample.csv -o results.csv
```

Expected CSV columns: `qt_ms` (or `qt`), and one of: `rr_ms`, `hr_bpm` (or `heart_rate`). Optional column: `sex` (default 'male').

### Python API

```python
from qtc import calculate_qtc, qtc_bazett, qt_dispersion, classify_qtc

# Calculate all four QTc formulas
result = calculate_qtc(qt_ms=400, rr_ms=1000, sex="male")
print(result)
# {
#   'qt_ms': 400.0, 'rr_ms': 1000.0, 'hr_bpm': 60.0, 'sex': 'male',
#   'qtc_bazett': 400.0, 'qtc_fridericia': 400.0,
#   'qtc_framingham': 400.0, 'qtc_hodges': 400.0,
#   'classification': 'normal'
# }

# Individual formula
qtc = qtc_bazett(qt_ms=400, rr_ms=1000)  # Returns 400.0

# QT dispersion
disp = qt_dispersion(qt_max_ms=420, qt_min_ms=390)  # Returns 30

# Classification
flag = classify_qtc(qtc_ms=460, sex="male")  # Returns 'prolonged'
```

---

## Testing

Run the full test suite:

```bash
pytest -v
```

Run specific test files:
```bash
pytest test_qtc.py -v
pytest tests/ -v
```

---

## Project Structure

```
ecg-qtc-calculator/
├── qtc.py              # Core QTc calculation formulas
├── cli.py              # Command-line interface
├── test_qtc.py         # Core module tests
├── sample.csv          # Sample input data
├── enrichment.py       # Enrichment feature modules
├── simulator.py        # Simulation runner
├── agents/             # Enterprise agent framework
│   ├── base.py         # Security, PHI guard, audit trail
│   ├── models.py       # Pydantic data models
│   ├── supervisor.py   # Multi-agent supervisor
│   ├── workers.py      # Specialized worker agents
│   ├── api.py          # FastAPI REST API
│   ├── metrics.py      # Prometheus metrics
│   └── ...
├── tests/              # Additional tests
├── web/                # Web dashboard
├── Dockerfile          # Container build
└── docker-compose.yml  # Container orchestration
```

---

## Security

- **PHI Guard:** Outbound data inspection blocking SSNs, MRNs, phone numbers, and patient identifiers
- **Audit Trail:** HMAC-SHA256 tamper-evident logging
- **Path Traversal Protection:** Input validation on file operations

Set `AUDIT_SECRET_KEY` environment variable for production use:
```bash
export AUDIT_SECRET_KEY="your-secure-random-key"
```

---

## License

MIT License - see [LICENSE](LICENSE) for details.
