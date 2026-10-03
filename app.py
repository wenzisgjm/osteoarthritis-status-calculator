from pathlib import Path
import json
import streamlit as st
import joblib
from prediction import FIELDS,MODEL,predict

ROOT=Path(__file__).resolve().parent
st.set_page_config(page_title='Osteoarthritis Status Calculator',page_icon='🧮',layout='wide')
st.markdown('''<style>.block-container{max-width:1200px;padding-top:2rem}h1{letter-spacing:-1px}div[data-testid="stMetric"]{background:#152a3d;color:#fff;padding:24px;border-radius:10px}div[data-testid="stMetric"] label{color:#c5d8e8}button[kind="primary"]{background:#114ca6}</style>''',unsafe_allow_html=True)
st.title('Osteoarthritis Status Calculator')
st.caption('NHANES 2011–2018 · Adults aged 65+ · Research edition')
st.write('Enter 19 health indicators to calculate the model-estimated probability of self-reported diagnosed osteoarthritis.')

@st.cache_resource
def load_pipeline():return joblib.load(ROOT/'oa_pipeline.joblib')

EXAMPLE={'RIDAGEYR':72,'RIAGENDR':2,'RIDRETH1':3,'DMDEDUC2':4,'smoking_status':1,'meets_guideline':1,'BMXBMI':29,'BMXWAIST':100,'mean_dbp':70,'LBXTR':120,'LBDLDL':111,'LBDHDD':55,'LBXSCH':190,'LBXGLU':105,'LBXSPH':3.5,'LBXSTP':7,'LBXLYPCT':30,'LBXMOPCT':8,'LBXNEPCT':60}
def set_example():
    for f in FIELDS:st.session_state[f['name']]=EXAMPLE[f['name']] if 'options' in f else float(EXAMPLE[f['name']])
    st.session_state['example']=True
    st.session_state.pop('probability',None)
def clear():
    for f in FIELDS:st.session_state[f['name']]=None
    st.session_state['example']=False
    st.session_state.pop('probability',None)
def changed():st.session_state.pop('probability',None);st.session_state['example']=False

left,right=st.columns([2,1],gap='large')
with left:
    a,b=st.columns(2)
    a.button('Load fictional example',on_click=set_example)
    b.button('Clear',on_click=clear)
    tabs=st.tabs(['01 Profile','02 Measurements','03 Lab results'])
    for tab,group in zip(tabs,['Profile','Measurements','Lab results']):
        with tab:
            if group=='Lab results':st.info('Use the units shown. Convert mmol/L results before entry.')
            cols=st.columns(2)
            fs=[f for f in FIELDS if f['group']==group]
            for i,f in enumerate(fs):
                with cols[i%2]:
                    if 'options' in f:
                        labels=dict(f['options'])
                        st.selectbox(f['label'],list(labels),format_func=lambda x,d=labels:d[x],index=None,key=f['name'],help=f.get('hint'),on_change=changed)
                    else:
                        st.number_input(f"{f['label']} ({f['unit']})",min_value=float(f['min']),max_value=float(f['max']),step=float(f['step']),value=None,key=f['name'],help=f.get('hint'),on_change=changed)
            if group=='Profile':
                with st.expander('Calculate my weekly activity target'):
                    st.caption('Include activity at work, during transport and in recreation. Enter zero if none.')
                    moderate=st.number_input('Moderate / transport minutes per week',min_value=0,max_value=10080,value=None,key='moderate')
                    vigorous=st.number_input('Vigorous minutes per week',min_value=0,max_value=10080,value=None,key='vigorous')
                    def set_activity():
                        m=st.session_state.moderate;v=st.session_state.vigorous
                        if m is not None and v is not None and m+v<=10080:
                            st.session_state.meets_guideline=int(m+2*v>=150);changed()
                    st.button('Use these activity totals',on_click=set_activity,disabled=moderate is None or vigorous is None or (moderate is not None and vigorous is not None and moderate+vigorous>10080))
    row={f['name']:st.session_state.get(f['name']) for f in FIELDS}
    count=sum(v is not None for v in row.values())
    st.caption(f'{count} of 19 complete · All indicators are required.')
    if st.button('Calculate probability',type='primary',disabled=count<19):
        try:st.session_state['probability']=predict(row,load_pipeline())
        except ValueError as exc:st.session_state.pop('probability',None);st.error(str(exc))
with right:
    st.subheader('Model estimate')
    probability=st.session_state.get('probability')
    st.metric('Self-reported diagnosed osteoarthritis',f'{probability:.1%}' if probability is not None else '—')
    if probability is not None:st.progress(probability)
    else:st.caption('Complete all indicators, then calculate your estimate.')
    if st.session_state.get('example'):st.info('Fictional example — replace these inputs with your own values.')
    st.write('This estimates an existing self-reported diagnosis, rather than future disease onset. It does not establish a diagnosis.')
    st.subheader('Study context')
    st.write('Development: 1,200 participants (2011–2016). Temporal validation: 402 participants (2017–2018).')
    st.write('Validation AUROC: **0.671** · AP: **0.506** · Brier: **0.218**.')
    st.caption('Developed in U.S. adults aged 65+ in the fasting subsample. Performance in other populations is unverified. Probability calibration and clinical thresholds have not been established.')
    with st.expander('Model and limitations'):
        st.write('L2-regularized logistic regression, C=0.01, 19 indicators. No low / medium / high risk labels are applied. Ages 80+ use the study’s top-coded value of 80.')
        st.write('Validation AUROC 95% CI: 0.619–0.726. Gender-specific AUROC: 0.700 in men and 0.573 in women. These are study performance estimates, not individual confidence intervals.')
        st.link_button('NHANES data source','https://www.cdc.gov/nchs/nhanes/index.htm')
st.divider()
st.caption('Research demonstration · Model v1.0.0 · Inputs are processed by this app but are not written to storage.')
