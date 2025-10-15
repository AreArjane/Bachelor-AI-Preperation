import os
import numpy as np
import pandas as pd
import yaml
from tqdm import tqdm

# -------- resolve ROOT and config --------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
CFG_PATH = os.path.join(ROOT, "configs", "base.yaml")

with open(CFG_PATH, "r", encoding="utf-8") as f:
    CFG = yaml.safe_load(f)

FS         = int(CFG["target_fs"])
WIN_SEC    = int(CFG["win_sec"])
STRIDE_SEC = int(CFG.get("stride_sec", WIN_SEC))
DROP_LAST  = bool(CFG.get("drop_last", True))

WIN   = FS * WIN_SEC
STRIDE = FS * STRIDE_SEC

# inputs from 01_resample_filter.py
INTERIM_DIR = os.path.join(ROOT, "data", "interim", f"{FS}hz")
IDX_NORM = os.path.join(INTERIM_DIR, f"{FS}hz_normal_index.csv")
IDX_AF   = os.path.join(INTERIM_DIR, f"{FS}hz_af_index.csv")

# outputs
WIN_DIR = os.path.join(ROOT, "data", "windows", f"{FS}hz_{WIN_SEC}s")
WIN_NORM_DIR = os.path.join(WIN_DIR, "normal")
WIN_AF_DIR   = os.path.join(WIN_DIR, "af")
os.makedirs(WIN_NORM_DIR, exist_ok=True)
os.makedirs(WIN_AF_DIR, exist_ok=True)

def slice_windows(x: np.ndarray, win: int, stride: int, drop_last: bool):
    """Yield (start_idx, window) for each window of shape [C, win]."""
    T = x.shape[1]
    if T < win:
        return
    start = 0
    while start + win <= T:
        yield start, x[:, start:start+win]
        start += stride
    if not drop_last and start < T:
       
        pad_len = start + win - T
        tail = np.pad(x[:, start:T], ((0,0),(0,pad_len)), mode="constant")
        yield start, tail

def process_class(index_csv: str, klass: str, out_dir: str):
    if not os.path.exists(index_csv):
        return pd.DataFrame()
    df = pd.read_csv(index_csv)
    rows = []
    for _, r in tqdm(df.iterrows(), total=len(df), desc=f"Windowing ({klass})"):
        recname = r["recname"]
        label   = int(r["label"])
        pid     = r["patient_id"]
        path    = r["path"]

        x = np.load(path).astype(np.float32)   
        for k, w in slice_windows(x, WIN, STRIDE, DROP_LAST):
            fname = f"{recname}_w{k:09d}.npy"  
            fpath = os.path.join(out_dir, fname)
            np.save(fpath, w)
            rows.append({
                "class": klass,
                "label": label,
                "recname": recname,
                "patient_id": pid,
                "fs": FS,
                "win_sec": WIN_SEC,
                "stride_sec": STRIDE_SEC,
                "path": fpath
            })
    return pd.DataFrame(rows)

meta_norm = process_class(IDX_NORM, "normal", WIN_NORM_DIR)
meta_af   = process_class(IDX_AF,   "af",     WIN_AF_DIR)

# per-class and combined indexes
idx_norm_out = os.path.join(WIN_DIR, f"{FS}hz_{WIN_SEC}s_normal_index.csv")
idx_af_out   = os.path.join(WIN_DIR, f"{FS}hz_{WIN_SEC}s_af_index.csv")
meta_norm.to_csv(idx_norm_out, index=False)
meta_af.to_csv(idx_af_out, index=False)

combined = pd.concat([meta_norm, meta_af], ignore_index=True)
combined = combined.sort_values(["class", "patient_id", "recname"])
idx_all_out = os.path.join(WIN_DIR, f"{FS}hz_{WIN_SEC}s_index.csv")
combined.to_csv(idx_all_out, index=False)

print(f"[02_window] normal -> {len(meta_norm)} windows -> {idx_norm_out}")
print(f"[02_window] af     -> {len(meta_af)} windows -> {idx_af_out}")
print(f"[02_window] combined -> {len(combined)} windows -> {idx_all_out}")
