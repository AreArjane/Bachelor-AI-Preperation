# AtriFibrilation 

## Dependencies
*Add to the requirement text and install with python virtual enviroment*
```bash
python -m venv venv
pip install -r requirement.txt
```

| Name           |
|----------------|
| wfdb           |
| numpy          |
| scipy          |
| pandas         |
| torch          |
| torchaudio     |
| scikit-learn   |
| tqdm           |


## Run

```bash

python main.py

```




### Create __init__.py if not presented

```bash

Get-ChildItem -Recurse -Directory src | ForEach-Object { New-Item -Path "$($_.FullName)\__init__.py" -ItemType File -Force }

```