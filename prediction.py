"""Validation and inference for two fixed development-set models."""
from pathlib import Path
import json
import math
import joblib
import pandas as pd

ROOT = Path(__file__).resolve().parent
FIELDS = json.loads((ROOT / 'fields.json').read_text(encoding='utf-8'))
MODELS = {key: json.loads((ROOT / file).read_text(encoding='utf-8')) for key, file in
          [('questionnaire', 'questionnaire_model.json'), ('full', 'model.json')]}
ARTIFACTS = {'questionnaire': 'questionnaire_pipeline.joblib', 'full': 'oa_pipeline.joblib'}
EVIDENCE = json.loads((ROOT / 'validation_metrics.json').read_text(encoding='utf-8'))


def fields_for(model_id):
    model = MODELS[model_id]
    names = set(model['numeric'] + model['categorical'])
    return [field for field in FIELDS if field['name'] in names]


def validate(record, model_id='questionnaire'):
    errors = []
    for field in fields_for(model_id):
        value = record.get(field['name'])
        if value is None or isinstance(value, bool):
            errors.append(f"{field['label']}: a value is required.")
            continue
        try:
            number = float(value)
        except (TypeError, ValueError, OverflowError):
            errors.append(f"{field['label']}: enter a valid number.")
            continue
        if not math.isfinite(number):
            errors.append(f"{field['label']}: enter a finite number.")
        elif 'options' in field:
            if number not in [option[0] for option in field['options']]:
                errors.append(f"{field['label']}: select a valid category.")
        elif (number < field['min'] or number > field['max']
              or (field['name'] == 'RIDAGEYR' and not number.is_integer())):
            errors.append(f"{field['label']}: enter a value from {field['min']} to {field['max']}.")
    if model_id == 'full' and not errors:
        if sum(float(record[name]) for name in ['LBXLYPCT', 'LBXMOPCT', 'LBXNEPCT']) > 100.5:
            errors.append('The three white blood cell percentages cannot add up to more than 100% (allowing for rounding).')
    return errors


def load_pipeline(model_id):
    return joblib.load(ROOT / ARTIFACTS[model_id])


def predict(record, model_id='questionnaire', pipeline=None):
    errors = validate(record, model_id)
    if errors:
        raise ValueError('\n'.join(errors))
    model = MODELS[model_id]
    names = model['numeric'] + model['categorical']
    row = {name: float(record[name]) for name in names}
    row['RIDAGEYR'] = min(80, row['RIDAGEYR'])
    fitted = pipeline if pipeline is not None else load_pipeline(model_id)
    if list(fitted.feature_names_in_) != names:
        raise ValueError('The loaded model does not match the selected predictor set.')
    return float(fitted.predict_proba(pd.DataFrame([row], columns=names))[0, 1])
