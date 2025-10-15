
import argparse
import subprocess
import sys
import os
from textwrap import dedent

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))

STEPS = [
    ("00_extract",         "Index WFDB recordings and write records_normal.csv / records_af.csv (+ combined index)"),
    ("01_resample_filter", "Bandpass + resample to target_fs + z-score, write interim arrays and indexes"),
    ("02_window",          "Slice fixed 1D windows (win_sec / stride_sec), write window arrays and indexes"),
    ("03_make_metadata",   "Assemble final data/metadata.csv for training"),
    # future step here:
    
]

def run_step(mod_name: str) -> int:
    """Run a module as `python -m src.data_prep.<mod_name>` and stream output."""
    print(f"\n=== Running: {mod_name} ===")
    try:
        proc = subprocess.run(
            [sys.executable, "-m", f"src.data_prep.{mod_name}"],
            cwd=ROOT,  
            check=False
        )
        return proc.returncode
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
        return 130
    except Exception as e:
        print(f"[error] Failed to run {mod_name}: {e}")
        return 1

def main():
    parser = argparse.ArgumentParser(
        prog="python -m src.data_preparation",
        description="Run 1D ECG data-preparation pipeline steps in order."
    )
    parser.add_argument(
        "--steps",
        nargs="+",
        choices=[name for name, _ in STEPS],
        help="Select specific steps to run (default: run all in order)."
    )
    parser.add_argument(
        "--yes", "-y",
        action="store_true",
        help="Skip confirmation prompt and run immediately."
    )
    args = parser.parse_args()

    # Which steps?
    selected = STEPS if not args.steps else [(n, d) for (n, d) in STEPS if n in args.steps]

    # Show plan
    print(dedent(f"""
    Project root: {ROOT}

    This will run the following data-prep steps {"(selected)" if args.steps else "(all)"}:

    """).strip())
    for i, (name, desc) in enumerate(selected, start=1):
        print(f"  {i}. {name:<20} - {desc}")

    # Confirm
    if not args.yes:
        reply = input("\nProceed? [y/N]: ").strip().lower()
        if reply not in ("y", "yes"):
            print("Aborted.")
            return

    # Execute in order
    for name, _ in selected:
        code = run_step(name)
        if code != 0:
            print(f"\n[stop] Step {name} failed with code {code}.")
            sys.exit(code)

    print("\n✅ All requested steps completed successfully.")

if __name__ == "__main__":
    main()
