# ECG Qtc Calculator

> **Domain:** Cardiovascular Medicine & Hemodynamic Analytics  
> **Reference Guidelines & Standards:** `AHA/ACC Practice Guidelines & ESC Clinical Standards`

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?logo=fastapi&logoColor=white)
![Audit Trail](https://img.shields.io/badge/Audit-HMAC--SHA256_Tamper--Evident-brightgreen.svg)
![Zero-PHI Guard](https://img.shields.io/badge/Guard-Zero--PHI_Outbound-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)

</div>

---

## 📖 What It Does

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

---

## ⚙️ Key Capabilities & Algorithmic Modules

### 🔬 Analytical Functions

- **`rr_from_hr()`**: Convert heart rate (bpm) to RR interval (ms).

>>> rr_from_hr(60)
1000.0
>>> rr_from_hr(75)
800.0
- **`hr_from_rr()`**: Convert RR interval (ms) to heart rate (bpm).

>>> hr_from_rr(1000)
60.0
- **`qtc_bazett()`**: Bazett formula: QTc = QT / sqrt(RR in seconds).

Reference: Bazett HC. Heart 1920;7:353-370.
Overcorrects at high heart rates, undercorrects at low heart rates.
- **`qtc_fridericia()`**: Fridericia formula: QTc = QT / (RR in seconds)^(1/3).

Reference: Fridericia LS. Acta Med Scand 1920;53:469-486.
Better performance at extreme heart rates than Bazett.
- **`qtc_framingham()`**: Framingham (Sagie) formula: QTc = QT + 0.154 * (1 - RR in seconds).

Reference: Sagie A, et al. Am J Cardiol 1992;70:797-801.
Linear regression correction from the Framingham Heart Study.

---

## 📐 Mathematical Formulation & Logic

```text
  Corrected QT interval (QTc) calculation using four standard formulas:
  """Bazett formula: QTc = QT / sqrt(RR in seconds).
  """Fridericia formula: QTc = QT / (RR in seconds)^(1/3).
  """Framingham (Sagie) formula: QTc = QT + 0.154 * (1 - RR in seconds).
  """Hodges formula: QTc = QT + 1.75 * (HR - 60).
```

---

## 💻 CLI Quickstart & Usage

### 1. Guided Interactive Mode
```bash
python cli.py
```

### 2. Direct Parameterized Evaluation
```bash
python cli.py --qt <value> --rr <value> --hr <value> --sex <value>
```

### Parameter Reference
- `--qt`: Specifies input measurement or parameter value.
- `--rr`: Specifies input measurement or parameter value.
- `--hr`: Specifies input measurement or parameter value.
- `--sex`: Specifies input measurement or parameter value.
- `--qt-max`: Specifies input measurement or parameter value.
- `--qt-min`: Specifies input measurement or parameter value.
- `--input`: Specifies input measurement or parameter value.
- `--output`: Specifies input measurement or parameter value.

### Input Data Schema

| Field | Description | Requirement |
|:------|:------------|:------------|
| `patient_id` | Parameter / observation metric | Required |
| `qt_ms` | Parameter / observation metric | Required |
| `rr_ms` | Parameter / observation metric | Required |
| `hr_bpm` | Parameter / observation metric | Required |

---

## 🛡️ Security & Enterprise Architecture

* **Zero-PHI Outbound Interceptor:** Active AST and regex inspection blocking SSNs, MRNs, phone numbers, and patient identifiers.
* **Tamper-Evident HMAC-SHA256 Audit Trail:** Chained, cryptographically signed logs for every evaluation and state transition.
* **Air-Gapped LLM Reasoning Adapter:** Agnostic integration for local Ollama instances (`llama3`, `mistral`), Claude 3.5 Sonnet, GPT-4o, and deterministic test mocks.
* **Active Learning Bayesian Calibration:** Dynamic tracker updating worker reliability weights and monitoring Brier calibration drift.
* **FastAPI & Prometheus Telemetry:** Exposes OpenAPI 3.1 REST endpoints and operational Prometheus metrics (`/metrics`).

---

## 🧪 Testing & Verification

Run the automated test suite:

```bash
pytest -v
```

Execute high-throughput batch simulation benchmarks:

```bash
python simulator.py --tasks 1000 --concurrency 8
```

---

## 🐳 Container Deployment

```bash
docker build -t ecg-qtc-calculator .
docker run -p 8000:8000 ecg-qtc-calculator
```
