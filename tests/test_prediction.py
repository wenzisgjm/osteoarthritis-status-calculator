import sys
from pathlib import Path
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from prediction import fields_for, predict, validate, load_pipeline, EVIDENCE

EXAMPLE = {'RIDAGEYR':72,'RIAGENDR':2,'RIDRETH1':3,'DMDEDUC2':4,'smoking_status':1,'meets_guideline':1,'BMXBMI':29,'BMXWAIST':100,'mean_dbp':70,'LBXTR':120,'LBDLDL':111,'LBDHDD':55,'LBXSCH':190,'LBXGLU':105,'LBXSPH':3.5,'LBXSTP':7,'LBXLYPCT':30,'LBXMOPCT':8,'LBXNEPCT':60}


class PredictionTests(unittest.TestCase):
    def test_incomplete_input_never_scores(self):
        for model_id in ['questionnaire', 'full']:
            for field in fields_for(model_id):
                row = dict(EXAMPLE)
                row.pop(field['name'])
                with self.subTest(model=model_id, field=field['name']):
                    with self.assertRaises(ValueError):
                        predict(row, model_id)

    def test_invalid_inputs_and_percentage_guard(self):
        for change in [{'RIDAGEYR':64}, {'RIDAGEYR':72.5}, {'RIDAGEYR':float('nan')},
                       {'RIDAGEYR':True}, {'RIAGENDR':3}, {'DMDEDUC2':9}]:
            for model in ['questionnaire', 'full']:
                with self.assertRaises(ValueError):
                    predict({**EXAMPLE, **change}, model)
        with self.assertRaises(ValueError):
            predict({**EXAMPLE, 'LBXNEPCT':90}, 'full')

    def test_questionnaire_does_not_require_unused_inputs(self):
        row = {f['name']:EXAMPLE[f['name']] for f in fields_for('questionnaire')}
        self.assertEqual(len(row), 6)
        self.assertEqual(validate(row), [])
        self.assertAlmostEqual(predict(row), predict(EXAMPLE), places=14)
        self.assertNotAlmostEqual(predict(row), predict(EXAMPLE, 'full'), places=4)

    def test_wrong_model_cannot_silently_score(self):
        with self.assertRaises(ValueError):
            predict(EXAMPLE, 'questionnaire', load_pipeline('full'))
        with self.assertRaises(KeyError):
            predict(EXAMPLE, 'unknown')

    def test_full_model_regression_and_top_coding(self):
        self.assertAlmostEqual(predict(EXAMPLE, 'full'), 0.42196631479896435, places=13)
        for model in ['questionnaire', 'full']:
            self.assertEqual(predict({**EXAMPLE, 'RIDAGEYR':80}, model),
                             predict({**EXAMPLE, 'RIDAGEYR':95}, model))

    def test_threshold_metrics_use_selected_model(self):
        q = EVIDENCE['models']['questionnaire']['thresholds'][1]
        f = EVIDENCE['models']['full']['thresholds'][1]
        self.assertEqual(q['threshold'], .37)
        self.assertAlmostEqual(q['sensitivity'], 65/148)
        self.assertAlmostEqual(f['sensitivity'], 70/148)
        for model in EVIDENCE['models'].values():
            for threshold in model['thresholds']:
                for metric in ['sensitivity','specificity','PPV','NPV']:
                    lo,hi=threshold[metric+'_ci']
                    self.assertTrue(0 <= lo < threshold[metric] < hi <= 1)


if __name__ == '__main__':
    unittest.main()
