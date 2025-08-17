import streamlit as st
from sidebar import render_sidebar
from login import login
render_sidebar()
# Check login
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    login()
    st.stop()
with st.sidebar:
    if st.session_state.get("authenticated"):
        st.markdown(f"👤 Logged in as: `{st.session_state['user']}`")
        if st.button("Logout"):
            st.session_state.clear()
            st.rerun()

st.markdown("""
    <div style='
        background-color: #4F8BF9;
        padding: 20px;
        border-radius: 80px;
        font-size: 80px;
        font-weight: 800;
        text-align: center;
        color: white;
        margin-bottom: 20px;'>
        Welcome to the Dashboard
    </div>
""", unsafe_allow_html=True)


