import os
import pandas as pd
import yaml

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
CFG_PATH = os.path.join(ROOT, "configs", "base.yaml")

with open(CFG_PATH, "r", encoding="utf-8") as f:
    CFG = yaml.safe_load(f)

FS = int(CFG["target_fs"])
WIN_SEC = int(CFG["win_sec"])
WIN_DIR = os.path.join(ROOT, "data", "windows", f"{FS}hz_{WIN_SEC}s")
IDX_ALL = os.path.join(WIN_DIR, f"{FS}hz_{WIN_SEC}s_index.csv")

df = pd.read_csv(IDX_ALL)

df = df.sample(frac=1.0, random_state=42).reset_index(drop=True)

out_csv = os.path.join(ROOT, "data", "metadata.csv")
os.makedirs(os.path.dirname(out_csv), exist_ok=True)
df.to_csv(out_csv, index=False)

print(f"[03_make_metadata] Final metadata -> {out_csv} ({len(df)} rows)")
