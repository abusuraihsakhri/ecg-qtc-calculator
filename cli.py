#!/usr/bin/env python3
"""CLI for ECG QTc Calculator."""
import argparse
import json
import sys

from qtc import calculate_qtc, qt_dispersion, process_csv


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="ecg-qtc-calculator",
        description="ECG QTc Calculator — Corrected QT interval by Bazett, Fridericia, Framingham, Hodges",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Single calculation
    single = subparsers.add_parser("single", help="Calculate QTc for a single patient")
    single.add_argument("--qt", type=float, required=True, help="QT interval in ms")
    single.add_argument("--rr", type=float, default=None, help="RR interval in ms")
    single.add_argument("--hr", type=float, default=None, help="Heart rate in bpm (used if --rr not given)")
    single.add_argument("--sex", default="male", choices=["male", "female"], help="Patient sex (default: male)")

    # QT dispersion
    disp = subparsers.add_parser("dispersion", help="Calculate QT dispersion")
    disp.add_argument("--qt-max", type=float, required=True, help="Maximum QT across leads (ms)")
    disp.add_argument("--qt-min", type=float, required=True, help="Minimum QT across leads (ms)")

    # Batch processing
    batch = subparsers.add_parser("batch", help="Batch process CSV file")
    batch.add_argument("-i", "--input", required=True, help="Input CSV path")
    batch.add_argument("-o", "--output", default="results.csv", help="Output CSV path")

    args = parser.parse_args(argv)

    if args.command == "single":
        if args.rr is None and args.hr is None:
            print("Error: must provide --rr or --hr", file=sys.stderr)
            return 1
        result = calculate_qtc(args.qt, rr_ms=args.rr, hr_bpm=args.hr, sex=args.sex)
        print(json.dumps(result, indent=2))
        return 0

    if args.command == "dispersion":
        qtd = qt_dispersion(args.qt_max, args.qt_min)
        result = {
            "qt_max_ms": args.qt_max,
            "qt_min_ms": args.qt_min,
            "qt_dispersion_ms": qtd,
            "normal": qtd < 40,
        }
        print(json.dumps(result, indent=2))
        return 0

    if args.command == "batch":
        results = process_csv(args.input, args.output)
        print(f"Processed {len(results)} records -> {args.output}")
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
