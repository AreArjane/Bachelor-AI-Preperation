import os

structure = [
    "af-detect/data/raw/ptbxl",
    "af-detect/data/raw/mitbih_afdb",
    "af-detect/data/interim",
    "af-detect/data/windows",
    "af-detect/src/data_prep",
    "af-detect/src/models",
    "af-detect/src/training",
    "af-detect/src/inference",
    "af-detect/configs",
    "af-detect/runs/fold_0",
    "af-detect/notebooks",
]

files = [
    "af-detect/data/metadata.csv",
    "af-detect/src/data_prep/00_extract.py",
    "af-detect/src/data_prep/01_resample_filter.py",
    "af-detect/src/data_prep/02_window.py",
    "af-detect/src/data_prep/03_make_metadata.py",
    "af-detect/src/models/cnn1d.py",
    "af-detect/src/training/dataset.py",
    "af-detect/src/training/train.py",
    "af-detect/src/training/eval.py",
    "af-detect/src/training/metrics.py",
    "af-detect/src/training/kfold_run.py",
    "af-detect/src/inference/predict.py",
    "af-detect/configs/base.yaml",
    "af-detect/README.md",
    "af-detect/requirements.txt",
]

for path in structure:
    os.makedirs(path, exist_ok=True)

for f in files:
    open(f, "a").close()

print("✅ Project structure created successfully!")
