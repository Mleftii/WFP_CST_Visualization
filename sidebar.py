import streamlit as st
from login import login
# Enforce login
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    login()
    st.stop()
def render_sidebar():
    st.markdown("""
        <style>
        [data-testid="stSidebarNav"]::before {
            content: "📋 M3NU";
            background-color: #4F8BF9;
            border-radius: 10px;
            padding: 2px;
            white-space: pre-wrap;
            display: block;
            margin-top: 20px;
            margin-bottom: 20px;
            font-size: 50px;
            font-weight: 700;
            color: white;
            padding-left: 10px;
        }
        </style>
    """, unsafe_allow_html=True)



