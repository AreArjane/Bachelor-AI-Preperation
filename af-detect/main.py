# af-detect/main.py
import os
import sys
import subprocess
from textwrap import dedent

ROOT = os.path.dirname(os.path.abspath(__file__))

def run(cmd):
    """Run a shell command and stream its output."""
    print(f"\n$ {' '.join(cmd)}\n")
    return subprocess.call(cmd, cwd=ROOT)

def run_data_preparation():

    print("\nData Preparation options:")
    print("  [1] Run ALL steps with confirmation")
    print("  [2] Run ALL steps without confirmation (--yes)")
    print("  [3] Choose specific steps (e.g., 00_extract 02_window)")

    choice = input("\nSelect (1/2/3): ").strip()

    base_cmd = [sys.executable, "-m", "src.data_preparation"]

    if choice == "1":
        # Interactive confirmation inside data_preparation
        return run(base_cmd)

    elif choice == "2":
        # Skip confirmation
        return run(base_cmd + ["--yes"])

    elif choice == "3":
        steps = input("Enter steps separated by space (e.g., 00_extract 01_resample_filter): ").strip()
        if not steps:
            print("No steps provided. Aborting.")
            return 1
        confirm = input("Skip confirmation? [y/N]: ").strip().lower() in ("y", "yes")
        cmd = base_cmd + ["--steps"] + steps.split()
        if confirm:
            cmd.append("--yes")
        return run(cmd)

    else:
        print("Invalid selection.")
        return 1

def main():
    while True:
        print(dedent("""
        ================================
        AF-Detect • Main Menu
        ================================
        1) Data Preparation (run pipeline)
        0) Exit
        """).strip())

        choice = input("Choose an option: ").strip()

        if choice == "1":
            code = run_data_preparation()
            if code != 0:
                print(f"\n❌ Data preparation exited with code {code}.")
            else:
                print("\n✅ Data preparation finished.")
        elif choice == "0":
            print("Bye!")
            break
        else:
            print("Unknown option.")

if __name__ == "__main__":
    # Ensure src is importable when using -m with relative paths
    sys.path.insert(0, os.path.join(ROOT, "src"))
    main()
