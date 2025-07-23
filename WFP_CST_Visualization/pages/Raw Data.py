import pandas as pd
import streamlit as st
from sidebar import render_sidebar
from login import login
render_sidebar()
# Enforce login
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    login()
    st.stop()
#st.title("🏠 Raw Data Interaction")
st.markdown("""
    <div style='
        background-color: #4F8BF9;
        border-radius: 10px;
        font-size: 60px;
        font-weight: 600;
        color: white;
        padding: 20px;
        margin-bottom: 10px;'>
         Raw Data Interaction
    </div>
""", unsafe_allow_html=True)

#loading data
st.title("📂 Upload WFP Data")
uploaded_file = st.file_uploader("Upload WFP CSV File", type=["csv"])
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    df_original = df.copy()
    st.success("✅ File uploaded successfully!")
    st.markdown("""
        <div style='
            background-color: #4F8BF9;
            border-radius: 20px;
            font-size: 30px;
            font-weight: 300;
            color: yellow;
            padding: 5px;
            margin-top: 60px;
            margin-left:0px;
            margin-right:250px;
            margin-bottom: 5px;'>
            Raw Data Viewer
        </div>
    """, unsafe_allow_html=True)
    st.dataframe(df)
    st.markdown("""
        <div style='
            background-color: #4F8BF9;
            border-radius: 20px;
            font-size: 30px;
            font-weight: 300;
            color: yellow;
            padding: 5px;
            margin-top: 60px;
            margin-left:0px;
            margin-right:250px;
            margin-bottom: 5px;'>
            Null Summary
        </div>
    """, unsafe_allow_html=True)
    def nullsummary():
        empty_cells = df.isnull().sum()
        null_summary=pd.DataFrame({'empty_cells':empty_cells,
                  'fractions':empty_cells.astype(str)+"/"""+str(len(df)),
                    'Percent Missing (%)':(empty_cells/len(df))*100})
        styled_df = null_summary.style.background_gradient(cmap="Blues")
        st.dataframe(styled_df)
    nullsummary()
    #Checking odd figures to replace
    st.markdown("""
        <div style='
            background-color: #4F8BF9;
            border-radius: 20px;
            font-size: 30px;
            font-weight: 300;
            color: yellow;
            padding: 5px;
            margin-top: 60px;
            margin-left:0px;
            margin-right:250px;
            margin-bottom: 5px;'>
            Outliers Check
        </div>
    """, unsafe_allow_html=True)
    tab1,tab2=st.tabs(['Unique Data in "activity_name"',"Unique Data in 'gender'"])
    with tab1:
        st.write(df['activity_name'].unique())
    with tab2:
        st.write(df['gender'].unique())
    #Change 'Not Defined' in gender to null
    df['gender']=df['gender'].replace('Not Defined',pd.NA)
    st.write('📌 Re-checking Null summary')
    nullsummary()
    st.markdown("""
        <div style='
            background-color: #4F8BF9;
            border-radius: 20px;
            font-size: 30px;
            font-weight: 300;
            color: yellow;
            padding: 5px;
            margin-top: 60px;
            margin-left:0px;
            margin-right:250px;
            margin-bottom: 5px;'>
            Duplicates Handling
        </div>
    """, unsafe_allow_html=True)
    st.metric('Unique households are:',df['household_identifier'].nunique())
    st.metric('Unique beneficiaries are:',df['beneficiary_identifier'].nunique())
    st.metric('Total Activities received are:',df['activity_name'].count())
    tab1,tab2=st.tabs(['📌 Duplicates with their counterparts','📌Just the duplicated rows'])
    with tab1:
        beneficiary_dups = df_original[df_original.duplicated(subset='beneficiary_identifier', keep=False)]
        st.write(beneficiary_dups)
    with tab2:
        beneficiary_dups2=df_original.duplicated(subset='beneficiary_identifier')
        st.write(df[beneficiary_dups2])


