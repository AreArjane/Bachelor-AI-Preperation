import os, re
import pandas as pd
import wfdb, yaml
from src.utils.find_root import ROOT 

CFG = yaml.safe_load(open(ROOT / "configs" / "base.yaml", "r", encoding="utf-8"))

OUT_DIR = ROOT / "data"
OUT_DIR.mkdir(parents=True, exist_ok=True)

def scan_root(ds_root:str, class_label:int, class_name:str):
    rows = []
    abs_root = ROOT / ds_root
    for dirpath, _, filenames in os.walk(abs_root):
        for fname in filenames:
            if not fname.endswith(".hea"):
                continue
            hea_path = os.path.join(dirpath, fname)
            base = os.path.splitext(hea_path)[0]     
            recname = os.path.basename(base)

            # must have .dat (waveform)
            if not os.path.exists(base + ".dat"):
                print(f"[{class_name}] skip (no .dat): {recname}")
                continue

            try:
                rec = wfdb.rdrecord(base)
            except Exception as e:
                print(f"[{class_name}] skip (rdrecord fail): {recname} -> {e}")
                continue

            fs = float(rec.fs)
            n_sig = rec.n_sig
            leads = ",".join(rec.sig_name)
            dur_sec = rec.sig_len / rec.fs if rec.fs else 0.0

            # patient id = first digits in recname (fallback: whole name)
            m = re.search(r"(\d+)", recname)
            pid = f"P{m.group(1)}" if m else f"P_{recname}"

            rows.append({
                "class": class_name,        # "normal" or "af"
                "label": int(class_label),  # 0 or 1
                "basepath": base,           # WFDB base path (no extension)
                "recname": recname,
                "patient_id": pid,
                "fs": fs,
                "n_leads": n_sig,
                "leads": leads,
                "dur_sec": dur_sec,
                "has_atr": int(os.path.exists(base + ".atr")),
                "has_qrs": int(os.path.exists(base + ".qrs")),
            })
    return pd.DataFrame(rows)

# scan both classes
df_norm = scan_root(CFG["class_roots"]["normal"]["root"],
                    CFG["class_roots"]["normal"]["label"], "normal")
df_af   = scan_root(CFG["class_roots"]["af"]["root"],
                    CFG["class_roots"]["af"]["label"], "af")

# distengish .csv Normal & AF
csv_norm = OUT_DIR / "records_normal.csv"
csv_af   = OUT_DIR / "records_af.csv"
df_norm.to_csv(csv_norm, index=False)
df_af.to_csv(csv_af, index=False)

# combination of Af & Normal
pd.concat([df_norm, df_af], ignore_index=True)\
  .sort_values(["class","patient_id","recname"])\
  .to_csv(OUT_DIR / "records_index.csv", index=False)

print(f"[00_extract] normal -> {len(df_norm)} rows -> {csv_norm}")
print(f"[00_extract] af     -> {len(df_af)} rows -> {csv_af}")
