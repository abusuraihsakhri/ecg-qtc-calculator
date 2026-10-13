# ECG QTc Calculator

### [Open the Live Application →](https://abusuraihsakhri.github.io/ecg-qtc-calculator/)

ECG QTc Calculator estimates rate-corrected QT intervals using four published correction formulas. It provides a **standalone browser calculator**, a standard-library Python API/CLI, batch CSV processing, and an optional FastAPI endpoint.

## Features

- Bazett, Fridericia, Framingham (Sagie), and Hodges QT corrections.
- Input measured QT in milliseconds and either RR in milliseconds or heart rate in beats/minute.
- Display four results and simplified adult QTc categories (based on Bazett); export a single browser calculation as CSV.
- Run a Python CLI for individual calculations, QT dispersion, and batch CSV input.
- Optional FastAPI `POST /api/qtc` endpoint; existing `/api/audit` endpoints are demonstration-only and **not clinically validated**.

## Browser application

The standalone application is in [web/index.html](web/index.html). It uses HTML, CSS and JavaScript, with **no Python runtime, server, third-party scripts, or API keys** required. Files may be served using any static web server.

GitHub Actions deploys the static calculator to the live application URL above.

Privacy: the static calculator processes entered measurements in the browser without storing or transmitting them. The optional backend and legacy audit features have different data-handling considerations; do not submit patient identifiers or protected health information to a publicly accessible server.

## Usage

Python 3.10 or later:

```bash
python cli.py single --qt 400 --hr 75 --sex male
python cli.py single --qt 350 --rr 600 --sex female
python cli.py dispersion --qt-max 420 --qt-min 390
python cli.py batch -i sample.csv -o results.csv
```

The CLI can also be used programmatically:

```python
from qtc import calculate_qtc
result = calculate_qtc(350, rr_ms=600, sex="male")
assert result["qtc_framingham"] == 411.6
```

CSV columns: `qt_ms` (or `qt`), and `rr_ms` or `hr_bpm` (or `heart_rate`). Optional: `sex` (default `male`). The batch output preserves original columns, adds QTc results, and reports row-specific errors.

## Formula definitions

All returned QTc values are in milliseconds. `RR_s = RR_ms / 1000`.

| Correction | Formula |
| --- | --- |
| Bazett | `QT_ms / sqrt(RR_s)` |
| Fridericia | `QT_ms / RR_s^(1/3)` |
| Framingham | `QT_ms + 154 × (1 - RR_s)` |
| Hodges | `QT_ms + 1.75 × (HR_bpm - 60)` |

**Important:** the Framingham coefficient of 0.154 is expressed in *seconds* in the original equation and equals **154 ms** when QT is measured in milliseconds. Inconsistent units can produce clinically meaningful errors.

The existing category thresholds are project-specific heuristics for adults: normal below 440/460 ms (male/female), borderline 440–450/460–470 ms, prolonged above 450/470 ms, and a separate warning at or above 500 ms. Threshold recommendations differ between sources and correction methods. QTc is not a standalone diagnosis; interpret it in context, particularly with wide QRS, variable RR intervals, or uncertain T-wave endpoints.

References: [AHA/ACCF/HRS QT guidance (2009)](https://www.jacc.org/doi/10.1016/j.jacc.2008.12.014); [AHA/ACCF statement on torsades prevention (2010)](https://pmc.ncbi.nlm.nih.gov/articles/PMC3056123/).

## Development and testing

Core calculations use only Python's standard library. Install test and optional API dependencies separately:

```bash
python -m pip install pytest fastapi uvicorn pydantic
python -m pytest -v
node tests/test_web.cjs
```

Node.js is needed only to run the browser formula tests, not to operate the browser calculator. The static page works in current Chrome, Firefox, Safari, and Edge; automated cross-browser compatibility has not yet been established.

To run the optional server:

```bash
uvicorn agents.api:app --reload
```

Open `http://localhost:8000/` for the browser application, or `http://localhost:8000/docs` for interactive FastAPI documentation. A `Dockerfile` and `docker-compose.yml` are also included. Before starting Docker Compose, set a strong random `AUDIT_SECRET_KEY` in the environment; the audit trail is **in-memory only**, not a persistent compliance record.

## License

[MIT](LICENSE).
