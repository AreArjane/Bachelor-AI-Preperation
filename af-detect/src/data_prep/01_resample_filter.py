# af-detect/src/data_prep/01_resample_filter.py
import os
import numpy as np
import pandas as pd
import wfdb
import yaml
from scipy.signal import butter, filtfilt, resample_poly
from fractions import Fraction
from tqdm import tqdm

# ------------ resolve ROOT and config ------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))    
CFG_PATH = os.path.join(ROOT, "configs", "base.yaml")

with open(CFG_PATH, "r", encoding="utf-8") as f:
    CFG = yaml.safe_load(f)

TARGET_FS = int(CFG["target_fs"])
BP = CFG["bandpass"]  # dict: low, high, order

# input CSVs from 00_extract.py
CSV_NORMAL = os.path.join(ROOT, "data", "records_normal.csv")
CSV_AF     = os.path.join(ROOT, "data", "records_af.csv")

# output dirs
INTERIM_DIR = os.path.join(ROOT, "data", "interim", f"{TARGET_FS}hz")
OUT_NORMAL_DIR = os.path.join(INTERIM_DIR, "normal")
OUT_AF_DIR     = os.path.join(INTERIM_DIR, "af")
os.makedirs(OUT_NORMAL_DIR, exist_ok=True)
os.makedirs(OUT_AF_DIR, exist_ok=True)

# ------------ helpers ------------
def bandpass(x, fs, low, high, order):
    ny = 0.5 * fs
    b, a = butter(order, [low/ny, high/ny], btype="band")
    return filtfilt(b, a, x, axis=-1)

def resample_to(x, fs_from, fs_to):
    if int(fs_from) == int(fs_to):
        return x.astype(np.float32)
    frac = Fraction(int(fs_to), int(fs_from)).limit_denominator()
    return resample_poly(x, frac.numerator, frac.denominator, axis=-1).astype(np.float32)

def zscore_per_lead(x):
    m = x.mean(axis=-1, keepdims=True)
    s = x.std(axis=-1, keepdims=True) + 1e-6
    return (x - m) / s

def load_signal(base_noext):
    rec = wfdb.rdrecord(base_noext)
    if rec.p_signal is not None:
        sig = rec.p_signal.T.astype(np.float32)  # [C, T]
    else:
        sig = rec.adc().T.astype(np.float32)
    return sig, float(rec.fs), rec.sig_name

def process_df(df: pd.DataFrame, klass: str, out_dir: str):
    rows = []
    if df is None or len(df) == 0:
        return pd.DataFrame(rows)

    for _, r in tqdm(df.iterrows(), total=len(df), desc=f"Clean+Resample ({klass})"):
        base = r["basepath"]  
        recname = r["recname"]
        label = int(r["label"])
        pid   = r["patient_id"]

        # load
        try:
            x, fs, lead_names = load_signal(base)
        except Exception as e:
            print(f"[skip] {klass}/{recname}: rdrecord failed -> {e}")
            continue

        # clean
        try:
            x = bandpass(x, fs, BP["low"], BP["high"], BP["order"])
        except Exception as e:
            print(f"[warn] bandpass failed for {recname} (using raw): {e}")

        try:
            x = resample_to(x, fs, TARGET_FS)
        except Exception as e:
            print(f"[skip] resample failed for {recname}: {e}")
            continue

        x = zscore_per_lead(x)

        # save
        out_path = os.path.join(out_dir, f"{recname}.npy")
        np.save(out_path, x)

        rows.append({
            "class": klass,
            "label": label,
            "recname": recname,
            "patient_id": pid,
            "fs": TARGET_FS,
            "leads": ",".join(lead_names),
            "n_samples": int(x.shape[1]),
            "path": out_path
        })

    return pd.DataFrame(rows)

# ------------ load indexes ------------
df_norm = pd.read_csv(CSV_NORMAL) if os.path.exists(CSV_NORMAL) else pd.DataFrame()
df_af   = pd.read_csv(CSV_AF)     if os.path.exists(CSV_AF)     else pd.DataFrame()

# ------------ process both classes ------------
meta_norm = process_df(df_norm, "normal", OUT_NORMAL_DIR)
meta_af   = process_df(df_af,   "af",     OUT_AF_DIR)

# ------------ write per-class and combined indexes ------------
idx_norm_path = os.path.join(INTERIM_DIR, f"{TARGET_FS}hz_normal_index.csv")
idx_af_path   = os.path.join(INTERIM_DIR, f"{TARGET_FS}hz_af_index.csv")
meta_norm.to_csv(idx_norm_path, index=False)
meta_af.to_csv(idx_af_path, index=False)

combined = pd.concat([meta_norm, meta_af], ignore_index=True)
combined = combined.sort_values(["class", "patient_id", "recname"])
idx_all_path = os.path.join(INTERIM_DIR, f"{TARGET_FS}hz_index.csv")
combined.to_csv(idx_all_path, index=False)

print(f"[01_resample_filter] normal -> {len(meta_norm)} rows -> {idx_norm_path}")
print(f"[01_resample_filter] af     -> {len(meta_af)} rows -> {idx_af_path}")
print(f"[01_resample_filter] combined -> {len(combined)} rows -> {idx_all_path}")
