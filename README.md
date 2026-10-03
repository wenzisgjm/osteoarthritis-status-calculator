# Osteoarthritis Status Calculator

Research companion for the NHANES 2011–2018 self-reported diagnosed osteoarthritis study. The fixed final model is a 19-variable L2-regularized logistic regression with C=0.01, fitted on the 2011–2016 development sample only. The 2017–2018 sample was not used to fit this artifact.

## Run locally

Use Python 3.12, then run these commands from this directory:

```sh
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS / Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Deploy

Upload this directory's contents to a new GitHub repository. In Streamlit Community Cloud, create an app using `app.py` as the entrypoint and Python 3.12. Dependencies are pinned to the exported model's runtime; do not upgrade scikit-learn without rebuilding and validating the model.

No training CSV, participant identifiers or participant examples are required at runtime. The model artifact contains the fitted preprocessing statistics and classifier coefficients. Only load this project's trusted `oa_pipeline.joblib`.

## Inputs and result

All 19 indicators are required; missing or invalid inputs stop scoring. Ages 80+ map to 80, as in the study. Laboratory units are displayed. Race/ethnicity and education use the study's NHANES categories. Smoking is coded 0=never, 1=former, 2=current. Activity is based on moderate-equivalent minutes across work, travel and recreation. The example is fictional.

The result estimates self-reported diagnosed osteoarthritis status. It does not predict future onset, diagnose disease, or establish clinical screening utility. No clinical threshold or high/medium/low risk label is applied. The study population was U.S. adults aged 65+ in the fasting subsample. Validation performance: AUROC 0.671, AP 0.506 and Brier 0.218. Calibration and transportability to other populations remain unverified.

The app processes form values on its server but does not write them to storage. Do not add input logging without an explicit data-handling policy.

## Validation

The exported model reproduced the manuscript's main LR temporal-validation metrics. Browser inference using the same exported coefficients and transformations was checked on all 1,602 study records, including missing values: maximum absolute probability difference 2.22e-16. The user-facing apps require complete inputs despite the pipeline retaining its fitted training imputer. Desktop/mobile interactions and Streamlit rendering, age top-coding and missing-input guards were tested.

The saved artifact is a fresh deterministic refit with the manuscript's fixed settings. The original notebook did not include a serialized model; this refit is not claimed to be byte-identical to an unavailable original artifact.
