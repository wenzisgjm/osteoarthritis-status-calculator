# Osteoarthritis Status Calculator

Research companion for the NHANES 2011–2018 self-reported diagnosed osteoarthritis study, version 2.0.0. The default questionnaire-only model uses six items; a full model uses 19 indicators. Both are L2-regularized logistic regressions with C=0.01, fitted on the 2011–2016 development sample only. The 2017–2018 sample was not used to fit or recalibrate either artifact.

Live app: https://osteoarthritis-status-calculator.streamlit.app/

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

No training CSV, participant identifiers or participant examples are required at runtime. The artifacts contain fitted preprocessing statistics and classifier coefficients. Only load this project's trusted `oa_pipeline.joblib` and `questionnaire_pipeline.joblib`.

## Inputs and result

The questionnaire model requires age, recorded gender, race/ethnicity, education, smoking status and aerobic activity guideline status. It requires no physical measurements or blood tests, but it was developed in the same fasting subsample. The full model additionally requires three anthropometric/clinical and ten laboratory measures. Missing or invalid inputs for the selected model stop scoring; the questionnaire model does not require unused laboratory values. Changing model or predictors clears the previous result.

Ages 80+ map to 80, as in the study. Laboratory units are displayed. Race/ethnicity and education use the study's NHANES categories. Smoking is coded 0=never, 1=former, 2=current. Activity is based on moderate-equivalent minutes across work, travel and recreation. The example is fictional.

The result estimates self-reported diagnosed osteoarthritis status. It does not predict future onset, diagnose disease, identify undiagnosed disease, or establish clinical screening utility. No clinical threshold or high/medium/low risk label is applied. The study population was U.S. adults aged 65+ in the fasting subsample. Validation performance is AUROC 0.642 / AP 0.481 / Brier 0.223 for the questionnaire model and 0.671 / 0.506 / 0.218 for the full model.

Both models underestimated the validation sample's average proportion with osteoarthritis: calibration-in-the-large was 0.157 (questionnaire) and 0.226 (full), with slopes 1.364 and 1.012. No intercept or slope update has been applied. Treat output as an exploratory aid to ranking for further assessment; individual absolute risks and transportability are not established. The predictor set was informed by previous work including the validation period, so this is not fully independent external validation.

The selected model's sensitivity, specificity, PPV and NPV at thresholds 0.30, 0.37 and 0.45 are displayed with Wilson 95% confidence intervals. These are descriptive validation-sample metrics, not personal confidence intervals or recommended cutoffs. The thresholds were selected post hoc using the same validation data. PPV and NPV depend on prevalence. See [MODEL_CARD.md](MODEL_CARD.md) for calibration/bootstrap assumptions and the questionnaire decision-curve range reconciliation.

The app processes form values on its server but does not write them to storage. Do not add input logging without an explicit data-handling policy.

## Validation

The original full-model export reproduced the manuscript's main LR temporal-validation metrics; its binary and parameters remain unchanged. The v2 release adds a separately fitted six-item pipeline and reproduces the manuscript's calibration point estimates and 2,000-resample stratified bootstrap confidence intervals for both models, together with threshold performance and Wilson intervals. Aggregate evidence is stored in `validation_metrics.json`. User-facing scoring requires complete inputs despite the pipelines retaining training imputers.

Run the prediction checks after installing requirements:

```sh
python -m unittest discover -s tests -v
```

The saved artifacts are deterministic development-set fits with the manuscript's fixed settings. The original notebook did not include serialized models; these artifacts are not claimed to be byte-identical to unavailable original files. Calibration-in-the-large confidence intervals condition on fixed case counts in the notebook's outcome-stratified resampling; survey weights and survey clustering were not incorporated.
