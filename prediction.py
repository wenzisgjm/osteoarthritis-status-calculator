from pathlib import Path
import json, math
import pandas as pd
import joblib

ROOT=Path(__file__).resolve().parent
MODEL=json.loads((ROOT/'model.json').read_text(encoding='utf-8'))
FIELDS=json.loads((ROOT/'fields.json').read_text(encoding='utf-8'))

def validate(record):
    errors=[]
    for f in FIELDS:
        value=record.get(f['name'])
        if value is None or isinstance(value,bool):
            errors.append(f"{f['label']}: a value is required.");continue
        try:v=float(value)
        except (TypeError,ValueError):
            errors.append(f"{f['label']}: enter a valid number.");continue
        if not math.isfinite(v):errors.append(f"{f['label']}: enter a finite number.");continue
        if 'options' in f:
            if v not in [o[0] for o in f['options']]:errors.append(f"{f['label']}: select a valid category.")
        elif v<f['min'] or v>f['max'] or (f['name']=='RIDAGEYR' and not v.is_integer()):
            errors.append(f"{f['label']}: enter a value from {f['min']} to {f['max']}.")
    if not errors and sum(float(record[c]) for c in ['LBXLYPCT','LBXMOPCT','LBXNEPCT'])>100.5:
        errors.append('The three white blood cell percentages cannot add up to more than 100%.')
    return errors

def predict(record, pipeline=None):
    errors=validate(record)
    if errors:raise ValueError('\n'.join(errors))
    row={name:float(record[name]) for name in MODEL['numeric']+MODEL['categorical']}
    row['RIDAGEYR']=min(80,row['RIDAGEYR'])
    pipeline=pipeline if pipeline is not None else joblib.load(ROOT/'oa_pipeline.joblib')
    return float(pipeline.predict_proba(pd.DataFrame([row]))[0,1])
