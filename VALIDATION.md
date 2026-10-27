# Release 2.0.0 validation

The app defaults to the six-item questionnaire model and optionally uses the original 19-predictor model. Both use development-set coefficients, C=0.01, and their own fitted preprocessing pipelines. Neither model was recalibrated on the temporal validation data. The full-model binary and metadata are unchanged from v1.0.0.

## Reproduced temporal validation

| Metric | Questionnaire | Full model |
|---|---:|---:|
| AUROC | 0.641879 | 0.671047 |
| AP | 0.481097 | 0.505759 |
| Brier | 0.222666 | 0.217940 |
| Calibration-in-the-large | 0.157283 | 0.226145 |
| Calibration slope | 1.363787 | 1.011714 |

Calibration and AUROC 95% intervals were recomputed using 2,000 outcome-stratified percentile resamples with the fitted model fixed, following the supplied notebook. The calibration-in-the-large intervals condition on fixed case counts. Sensitivity, specificity, PPV and NPV at 0.30, 0.37 and 0.45 were recomputed, with Wilson 95% confidence intervals. Full-precision aggregate results are in `validation_metrics.json`.

The isolated test environment used the deployment's pinned scikit-learn 1.7.2, NumPy 2.3.5, pandas 3.0.1 and SciPy 1.16.2. Saved pipelines were compared with private build-time predictions for all 402 validation observations: maximum differences were at most 1.12e-16. Complete-input app inference was checked separately on 398 questionnaire-complete and 350 full-model-complete observations, with maximum differences at most 1.12e-16. Pipeline checks retain fitted imputation for reproducing the study; public app scoring rejects incomplete inputs.

## Functional checks

- Six prediction tests cover each missing predictor, invalid/nonfinite/category values, invalid white blood cell percentages, wrong-pipeline rejection, age top-coding, the original full-model probability and model-specific threshold metrics.
- Streamlit AppTest executed both models, default model selection, example loading, calculation, model switching, predictor changes, clear, missing-input blocking, the activity helper and threshold-table switching, with no app exceptions.
- The fictional example gives 46.4% for the questionnaire model and 42.2% for the full model. These are illustrative model outputs, not clinical interpretation.

## Decision curve reconciliation

The notebook defines superiority as net benefit more than 0.01 above the better default strategy across the longest continuous threshold grid interval. Reproduction gives 0.25–0.47 for the questionnaire model and 0.24–0.51 for the full model. For the questionnaire model, 0.23 is an isolated qualifying point and 0.24 does not pass. The manuscript's 0.23–0.47 questionnaire range therefore needs reconciliation; it was not copied into the app as a continuous range.

Tests above verify local code and saved artifacts. A GitHub commit or HTTP page response alone does not establish that the live Streamlit service has loaded this release. Desktop/mobile browser layout was not independently rechecked for this release.

Raw datasets, participant identifiers and individual validation predictions are not included in the repository.
