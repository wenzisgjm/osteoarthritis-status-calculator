import pandas as pd
import streamlit as st
from prediction import FIELDS, EVIDENCE, fields_for, predict, load_pipeline

VERSION = '2.0.0'
LABELS = {'questionnaire': 'Questionnaire-only (6 items)', 'full': 'Full model (19 predictors)'}
st.set_page_config(page_title='Osteoarthritis Status Calculator', page_icon='🧮', layout='wide')
st.markdown('''<style>
.block-container{max-width:1200px;padding-top:2rem}h1{letter-spacing:-1px}
div[data-testid="stMetric"]{background:#152a3d;color:#fff;padding:24px;border-radius:10px}
div[data-testid="stMetric"] label{color:#c5d8e8}
button[kind="primary"]{background:#114ca6}
</style>''', unsafe_allow_html=True)
st.title('Osteoarthritis Status Calculator')
st.caption('NHANES 2011–2018 · Adults aged 65+ · Research edition')
st.write('Estimate self-reported diagnosed osteoarthritis status using questionnaire items or the full set of health indicators.')

EXAMPLE = {'RIDAGEYR':72,'RIAGENDR':2,'RIDRETH1':3,'DMDEDUC2':4,'smoking_status':1,'meets_guideline':1,'BMXBMI':29,'BMXWAIST':100,'mean_dbp':70,'LBXTR':120,'LBDLDL':111,'LBDHDD':55,'LBXSCH':190,'LBXGLU':105,'LBXSPH':3.5,'LBXSTP':7,'LBXLYPCT':30,'LBXMOPCT':8,'LBXNEPCT':60}


def changed():
    st.session_state.pop('result', None)
    st.session_state['example'] = False


def set_example():
    for field in fields_for(st.session_state.get('model_id', 'questionnaire')):
        value = EXAMPLE[field['name']]
        st.session_state[field['name']] = value if 'options' in field else float(value)
    changed()
    st.session_state['example'] = True


def clear():
    for field in FIELDS:
        st.session_state[field['name']] = None
    for name in ['moderate', 'vigorous']:
        st.session_state[name] = None
    changed()


def set_activity():
    moderate = st.session_state.get('moderate')
    vigorous = st.session_state.get('vigorous')
    if moderate is not None and vigorous is not None and moderate + vigorous <= 10080:
        st.session_state['meets_guideline'] = int(moderate + 2 * vigorous >= 150)
        changed()


@st.cache_resource
def cached_pipeline(model_id):
    return load_pipeline(model_id)


def interval(value, ci, percent=False):
    if percent:
        return f'{value:.0%} ({ci[0]:.0%}–{ci[1]:.0%})'
    return f'{value:.2f} ({ci[0]:.2f}–{ci[1]:.2f})'


model_id = st.radio('Choose a model', list(LABELS), format_func=LABELS.get,
                    index=0, horizontal=True, key='model_id', on_change=changed)
selected_fields = fields_for(model_id)
evidence = EVIDENCE['models'][model_id]
if model_id == 'questionnaire':
    st.info('Six questionnaire items only. No physical measurements or blood tests are required. This model was also developed in the NHANES fasting subsample.')
else:
    st.info('All 19 indicators are required, including physical measurements and laboratory results.')

left, right = st.columns([2, 1], gap='large')
with left:
    a, b = st.columns(2)
    a.button('Load fictional example', on_click=set_example)
    b.button('Clear', on_click=clear)
    groups = ['Profile'] if model_id == 'questionnaire' else ['Profile', 'Measurements', 'Lab results']
    tabs = st.tabs([f'{i+1:02} {group}' for i, group in enumerate(groups)])
    for tab, group in zip(tabs, groups):
        with tab:
            if group == 'Lab results':
                st.info('Use the units shown. Convert mmol/L results before entry.')
            cols = st.columns(2)
            for i, field in enumerate(f for f in selected_fields if f['group'] == group):
                with cols[i % 2]:
                    if 'options' in field:
                        labels = dict(field['options'])
                        st.selectbox(field['label'], list(labels), format_func=lambda x, d=labels: d[x],
                                     index=None, key=field['name'], help=field.get('hint'), on_change=changed)
                    else:
                        st.number_input(f"{field['label']} ({field['unit']})", min_value=float(field['min']),
                                        max_value=float(field['max']), step=float(field['step']), value=None,
                                        key=field['name'], help=field.get('hint'), on_change=changed)
            if group == 'Profile':
                with st.expander('Calculate my weekly activity target'):
                    st.caption('Include activity at work, during transport and in recreation. Enter zero if none.')
                    moderate = st.number_input('Moderate / transport minutes per week', min_value=0,
                                               max_value=10080, value=None, key='moderate')
                    vigorous = st.number_input('Vigorous minutes per week', min_value=0,
                                               max_value=10080, value=None, key='vigorous')
                    invalid_activity = moderate is None or vigorous is None or moderate + vigorous > 10080
                    st.button('Use these activity totals', on_click=set_activity, disabled=invalid_activity)
    row = {field['name']: st.session_state.get(field['name']) for field in selected_fields}
    count = sum(value is not None for value in row.values())
    st.caption(f'{count} of {len(selected_fields)} complete · All inputs for this model are required.')
    if st.button('Calculate probability', type='primary', disabled=count < len(selected_fields)):
        try:
            probability = predict(row, model_id, cached_pipeline(model_id))
            st.session_state['result'] = {'model_id': model_id, 'probability': probability}
        except ValueError as exc:
            st.session_state.pop('result', None)
            st.error(str(exc))
with right:
    st.subheader('Model estimate')
    result = st.session_state.get('result')
    probability = result['probability'] if result and result['model_id'] == model_id else None
    st.caption(LABELS[model_id])
    st.metric('Self-reported diagnosed osteoarthritis', f'{probability:.1%}' if probability is not None else '—')
    if probability is not None:
        st.progress(probability)
    else:
        st.caption('Complete the selected model’s inputs, then calculate your estimate.')
    if st.session_state.get('example'):
        st.info('Fictional example — replace these inputs with your own values.')
    st.warning('Both models underestimated the average proportion with osteoarthritis in temporal validation. No intercept update has been applied for a target population. Use outputs as exploratory aids to ranking for further assessment, not as established individual risks.')
    st.caption('The outcome is an existing self-reported diagnosis. This does not predict future onset, identify undiagnosed disease, or establish a clinical diagnosis.')
    st.subheader('Study context')
    st.write('Development: 1,200 participants (2011–2016). Temporal validation: 402 participants, including 148 cases (2017–2018).')
    st.write(f"AUROC: **{evidence['AUROC']:.3f}** · AP: **{evidence['AP']:.3f}** · Brier: **{evidence['Brier']:.3f}**.")
    with st.expander('Calibration and limitations'):
        st.write('Calibration-in-the-large: ' + interval(evidence['CITL'], evidence['CITL_ci']))
        st.write('Calibration slope: ' + interval(evidence['slope'], evidence['slope_ci']))
        st.caption('Parentheses show 95% percentile intervals from 2,000 outcome-stratified bootstrap resamples with fixed case counts. These condition on the validation case proportion and do not account for survey clustering.')
        st.write(f"Mean predicted probability: {evidence['mean_predicted']:.1%}; observed proportion: {evidence['observed']:.1%}.")
        st.write('Both models use L2 logistic regression, C=0.01, fitted on the development sample only. Ages 80+ use a value of 80. Validation calibration was assessed, not used to change either model.')
        st.write('Developed in U.S. adults aged 65+ in the fasting subsample; applicability elsewhere is unverified. Predictor choice was informed by previous work including the validation period, so this was not fully independent external validation. Analyses were unweighted.')
        if model_id == 'full':
            st.write('Full-model validation AUROC: 0.700 in men and 0.573 in women. Subgroup results describe this validation sample; they are not individual uncertainty intervals.')
        st.link_button('NHANES data source', 'https://www.cdc.gov/nchs/nhanes/index.htm')

st.divider()
st.subheader('Performance at descriptive thresholds')
st.caption(f'{LABELS[model_id]} · 2017–2018 validation · 402 participants, 148 cases')
st.write('These thresholds were selected after inspecting the same validation data. They are descriptive research examples, not recommended clinical cutoffs. No high / medium / low risk label is assigned.')
show_ci = st.checkbox('Show 95% confidence intervals', value=True, key='show_threshold_ci')
table = []
for source in evidence['thresholds']:
    item = {'Threshold': f"{source['threshold']:.0%}", 'Positive per 100': f"{source['positive_per_100']:.0f}"}
    for name, label in [('sensitivity', 'Sensitivity'), ('specificity', 'Specificity'), ('PPV', 'PPV'), ('NPV', 'NPV')]:
        item[label] = interval(source[name], source[name + '_ci'], percent=True) if show_ci else f'{source[name]:.0%}'
    table.append(item)
st.dataframe(pd.DataFrame(table), hide_index=True, width='stretch')
st.caption('Sensitivity: proportion of cases classified positive. Specificity: proportion of controls classified negative. PPV / NPV: positive / negative predictive value; both depend on prevalence. Parentheses show Wilson 95% confidence intervals for validation performance, not uncertainty in an individual estimate.')
with st.expander('Decision curve evidence'):
    st.write('The full model exceeded the better of assess-all and assess-none by more than 0.01 net benefit over the continuous threshold grid range 0.24–0.51. For the questionnaire-only model, the reproduced longest continuous range is 0.25–0.47. These results used the same validation sample, before intercept updating, and do not establish a clinical decision rule.')
    st.caption('Thresholds above are displayed for study comparison only. No specific follow-up assessment was evaluated.')
st.caption(f'Research demonstration · Model v{VERSION} · Inputs are processed by this app but are not written to storage.')
