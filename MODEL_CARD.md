# Model v2.0.0

The default questionnaire-only model uses six items: age, recorded gender, race/ethnicity, education, smoking status and aerobic activity guideline status. The full model uses these six plus three anthropometric/clinical and ten laboratory variables. Both are L2 logistic regressions with C=0.01, max_iter=5000 and seed 42.

Both models were fitted only on the 2011–2016 development sample (1,200 participants); 2017–2018 supplies temporal validation (402 participants; 148 cases). Numerical predictors were median-imputed and standardized; categorical predictors were mode-imputed and fully one-hot encoded. The app requires complete inputs for the selected model despite retaining training imputers. Ages 80+ are encoded as 80. The questionnaire model was exported for this release with scikit-learn 1.7.2. The existing full-model binary and parameters are unchanged. No validation-based intercept or slope update was applied.

The target is existing self-reported diagnosed osteoarthritis versus reporting no arthritis in U.S. adults aged 65+ eligible for the NHANES fasting subsample. Other arthritis types were excluded. This is not a future-onset or clinical diagnostic model. Survey weights and cluster-aware resampling were not used. Predictor choice was informed by prior work including the validation period; this is not fully independent external validation.

Validation calibration and threshold metrics are in validation_metrics.json. Calibration intervals condition on the notebook's outcome-stratified bootstrap with fixed case counts. Thresholds 0.30, 0.37 and 0.45 were selected post hoc using the same validation data; performance is descriptive and may be optimistic for prospective use. PPV and NPV depend on prevalence. These values are not individual confidence intervals and do not define recommended clinical thresholds.

For decision curves, the code defines superiority as net benefit more than 0.01 above the better of assess-all and assess-none across the longest continuous grid interval. Reproduction gives 0.25–0.47 for the questionnaire model (0.23 is isolated; 0.24 does not pass), and 0.24–0.51 for the full model. The questionnaire manuscript range 0.23–0.47 requires reconciliation; the app does not present it as an established clinical range.

The app does not persist form inputs. Raw data, participant records and individual reference predictions are excluded from this repository.
