
import pandas as pd
import streamlit as st
from altair import value
from sidebar import render_sidebar
from login import login
import matplotlib.pyplot as plt
import plotly.express as px
from matplotlib_venn import venn3
from upsetplot import UpSet, from_memberships
from collections import Counter

render_sidebar()
# Enforce login
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    login()
    st.stop()
st.markdown("""
    <div style='
        background-color: #4F8BF9;
        border-radius: 10px;
        padding: 20px;
        font-size: 60px;
        font-weight: 600;
        color: white;
        margin-bottom: 10px;'>
        🏠 Visuals
    </div>
""", unsafe_allow_html=True)
st.title("📂 Upload WFP Data")
uploaded_file = st.file_uploader("Upload WFP CSV File", type=["csv"])
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    df_original = df.copy()
    st.success("✅ File uploaded successfully!")
    #Total Household Members
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
            📊 Households Summary Stats
        </div>
    """, unsafe_allow_html=True)
    #recalculating age so it appears in filters
    def agecalculation(df):
        df['date_of_birth']=pd.to_datetime(df['date_of_birth'],errors='coerce')
        today=pd.Timestamp.today()
        #df['age']=(today-df['date_of_birth']).dt.days//365 -- not exact age
        df['age'] = (
            today.year - df['date_of_birth'].dt.year
            - ((today.month < df['date_of_birth'].dt.month) |
               ((today.month == df['date_of_birth'].dt.month) & (today.day < df['date_of_birth'].dt.day))))
        age_bins = [0, 5, 10, 15, 18, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100, float('inf')]
        age_labels = ['0-4yrs', '5-9yrs', '10-14yrs', '15-17yrs', '18-19yrs', '20-24yrs', '25-29yrs', '30-34yrs', '35-39yrs',
                      '40-44yrs', '45-49yrs', '50-54yrs', '55-59yrs', '60-64yrs', '65-69yrs', '70-74yrs', '75-79yrs',
                      '80-84yrs', '85-89yrs', '90-94yrs', '95-99yrs', '100+yrs']
        df['age_cohort']=pd.cut(df['age'],bins=age_bins,labels=age_labels,right=False).sort_index()
    agecalculation(df)
    #household_members=df.groupby('household_identifier')['beneficiary_identifier'].nunique()
    st.sidebar.header("🔍 Filter Options")
    df['gender'] = df['gender'].replace('Not Defined',pd.NA)#representing null as null
    gender_filter = st.sidebar.multiselect(
        "Select Gender(s):",options=df['gender'].dropna().unique(), default=df['gender'].dropna().unique())
    activity_filter = st.sidebar.multiselect(
        "Select Activity(s):",options=df['activity_name'].unique(),default=df['activity_name'].unique())
    # --- Apply Filters ---
    filtered_df = df[
            (df['gender'].isin(gender_filter)) &
            (df['activity_name'].isin(activity_filter))]
    # --- Compute Household Member Stats ---
    household_members=filtered_df.groupby('household_identifier')['beneficiary_identifier'].nunique()
    #st.write(household_members)
    total_households = household_members.count()
    total_beneficiaries = filtered_df['beneficiary_identifier'].nunique()
    max_members = household_members.max()
    min_members = household_members.min()
    common_number_of_members = household_members.mode()
    average_members = household_members.mean()
    # --- Percentages ---
    percent_max = (max_members / average_members) * 100
    percent_min = (min_members / average_members) * 100
    # --- Tabs ---
    tab1, tab2 = st.tabs(["📊 Summary", "📈 Charts"])
    # -----------Summary Metrics --------
    with tab1:
        st.subheader("📌 Household Stats (Filtered View)")
        col1,col2,col3 = st.columns(3)
        with col1:
            st.metric("🏠 Unique Households", value=total_households)
            st.metric("🔼 Max Members", value=max_members, delta=f"{percent_max:.1f}% above avg")
        with col2:
            st.metric("👥 Unique Beneficiaries", value=total_beneficiaries)
            st.metric("🔻 Min Members", value=min_members, delta=f"{percent_min:.1f}% of avg")
        with col3:
                with st.expander('Average No. of Members per Household'):
                    st.metric(label="🧮Average per household", value=int(average_members))
                with st.expander('Most Common No. of Members per Household'):
                    st.metric(label="🎯Mode per household", value=common_number_of_members)
    with tab2:
        st.subheader("📉 Household Size Distribution")
        member_df = household_members.reset_index(name='members_count')
        #st.write(member_df)
        fig = px.histogram(member_df,x='members_count',nbins=15,title="Distribution of Members per Household",
            labels={'members_count': 'Members per Household'},color_discrete_sequence=['indigo','blue'])
        fig.update_layout(xaxis_title='Number of Members', yaxis_title='Number of Households', bargap=0.3)
        st.plotly_chart(fig, use_container_width=True)
    #Age Distribution
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
            📌 Age Summary
        </div>
    """, unsafe_allow_html=True)
    tab1,tab2,tab3=st.tabs(["📊 Summary", "📈 Charts", "🧮 Raw Data Glimpse"])
    from datetime import datetime
    #df['age']=(today-df['date_of_birth']).dt.days//365 -- not exact age
    agecalculation(df)
    age_summary=df['age_cohort'].value_counts().sort_index()
    # Group the data by age cohort and gender
    grouped = filtered_df.groupby(['age_cohort', 'gender']).size().reset_index(name='beneficiaries')
    oldest=filtered_df['age'].max()
    youngest=filtered_df['age'].min()
    average_age=filtered_df['age'].mean()
    mode_age=filtered_df['age'].mode()
    adults = filtered_df[filtered_df['age'] >= 18]['beneficiary_identifier'].nunique()
    children=filtered_df[filtered_df['age']<18]['beneficiary_identifier'].nunique()
    with tab1:
        col1,col2,col3=st.columns(3)
        with col1:
            st.metric('Number of Adults (18+)', value=adults)
            st.metric('Number of children (below 18 yrs)', value=children)
        with col2:
            st.metric('Eldest beneficiary', value=f"{int(oldest)} yrs")
            st.metric('Youngest beneficiary', value=f"{int(youngest)} yrs")
        with col3:
            st.metric('average',value=F"{int(average_age)} yrs")
    with tab2:
        tab2_1,tab2_2,tab2_3=st.tabs(['Sunburst chart','Treemap chart','Bar graph'])
        with tab2_1:
            sunburst = st.checkbox('See Sunburst chart?')
            if sunburst:
                fig = px.sunburst(
                    grouped,
                    path=['age_cohort', 'gender'],
                    values='beneficiaries',
                    title='Sunburst Chart: Beneficiaries by Age and Gender',
                    color='gender',
                    color_discrete_sequence=px.colors.qualitative.Set2
                )
                st.plotly_chart(fig, use_container_width=True)
        with tab2_2:
            treemap = st.checkbox('See Treemap chart?')
            if treemap:
                fig = px.treemap(
                    grouped,
                    path=['age_cohort', 'gender'],
                    values='beneficiaries',
                    title='Treemap: Beneficiaries by Age and Gender',
                    color='gender',
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                st.plotly_chart(fig, use_container_width=True)
        with tab2_3:
            bar = st.checkbox('See Bar graph?')
            if bar:
                # Create the grouped bar chart
                fig = px.bar(grouped, x='age_cohort', y='beneficiaries', color='gender', barmode='group',
                             color_discrete_sequence=['indigo', 'blue'],
                             title='Total Beneficiaries by Age and Gender',
                             hover_data=['gender', 'age_cohort', 'beneficiaries'])
                fig.update_layout(bargap=0.1)
                st.plotly_chart(fig, use_container_width=False)
    with tab3:
        col1,col2,col3=st.columns(3)
        with col1:
            st.write(age_summary)
        with col3:
            st.write(grouped)
    #Gender
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
            📌 Gender Summary
        </div>
    """, unsafe_allow_html=True)
    agecalculation(df)
    tab3, tab4 = st.tabs(["📊 Summary", "📈 Charts"])
    with tab3:
        col1,col2,col3=st.columns(3)
        with col1:
            females=filtered_df[filtered_df['gender']=='Female']['beneficiary_identifier'].nunique()
            st.metric('Total Females',value=females)
        with col2:
            males = filtered_df[filtered_df['gender'] == 'Male']['beneficiary_identifier'].nunique()
            st.metric('Total Males',value=males)
    with tab4:
        gender_df = pd.DataFrame({
            'gender': ['Male', 'Female'],
            'count': [males, females]})
        # Create the pie chart
        fig = px.pie(gender_df, names='gender', values='count', title='Gender Distribution of Beneficiaries')
        # Display the chart in Streamlit
        fig.update_traces(textinfo='percent+label', textposition='inside')
        st.plotly_chart(fig, use_container_width=True)
    #Extent to which beneficiaries appear in more than one activity
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
            📌 Activities Summary
        </div>
    """, unsafe_allow_html=True)
    tab5,tab6,tab7=st.tabs(["📊 Summary", "📈 Charts","🧮 Raw Data Glimpse"])
    activity_counts = filtered_df.groupby('beneficiary_identifier')['activity_name'].nunique()
    multiple_activities=[activity_counts>1]
    multi_activity_df = filtered_df[filtered_df['beneficiary_identifier'].isin(activity_counts[activity_counts > 1].index)]

    with tab5:
        total_activities=filtered_df['activity_name'].value_counts().reset_index()
        total_activities.columns=['Activity','Count']
        col1,col2,col3=st.columns(3)
        with col1:
            st.metric('Activity 1:',value=(filtered_df['activity_name']=='Activity 1').sum())
        with col2:
            st.metric('Activity 2:',value=(filtered_df['activity_name']=='Activity 2').sum())
            st.metric('\u200b', value='')
            st.metric('Total Activities Done:',value=(filtered_df['activity_name'].count()))
        with col3:
            st.metric('Activity 3:',value=(filtered_df['activity_name']=='Activity 3').sum())
    with tab6:
        tab1,tab2,tab3=st.tabs(['Pie Chart','Venn Diagram','Upset Plot'])
        with tab1:
            # Create pie chart
            fig = px.pie(total_activities, names='Activity', values='Count',
                         title='Activities Distribution of Beneficiaries')
            fig.update_traces(textinfo='percent+label', textposition='inside')
            # Display chart
            st.plotly_chart(fig, use_container_width=True)
        with tab2:

            # Sets of beneficiaries per activity
            a1 = set(filtered_df[filtered_df['activity_name'] == 'Activity 1']['beneficiary_identifier'])
            a2 = set(filtered_df[filtered_df['activity_name'] == 'Activity 2']['beneficiary_identifier'])
            a3 = set(filtered_df[filtered_df['activity_name'] == 'Activity 3']['beneficiary_identifier'])
            # Plot the Venn diagram
            fig, ax = plt.subplots()
            venn3([a1, a2, a3], set_labels=('Activity 1', 'Activity 2', 'Activity 3'), ax=ax)
            ax.set_title("Beneficiaries by Overlapping Activities")
            # Display in Streamlit
            st.pyplot(fig)
        with tab3:
            # Group activities per beneficiary
            beneficiary_activities = df.groupby('beneficiary_identifier')['activity_name'].unique()
            # Convert to tuple of unique activity sets
            memberships = [tuple(sorted(set(acts))) for acts in beneficiary_activities]
            # Count combinations
            membership_counts = Counter(memberships)
            # Convert dict keys and values to lists
            keys = list(membership_counts.keys())
            values = list(membership_counts.values())
            # Create UpSet plot data
            data = from_memberships(keys, data=values)
            # Plot
            UpSet(data).plot()
            plt.title("Activity Participation Overlap")
            st.pyplot(plt)
    with tab7:
        st.write('Total Activities done:',filtered_df['activity_name'].count(),filtered_df['activity_name'].value_counts().sort_index())
        st.subheader('Beneficiaries with multiple activities')
        st.dataframe(multi_activity_df)