import streamlit as st

# Hardcoded credentials (or load from file/db securely in production)
VALID_USERS = {
    "admin": "admin123",
    "user1": "pass456"
}
def login():
    st.title("🔐 Login Page")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username in VALID_USERS and VALID_USERS[username] == password:
            st.session_state["authenticated"] = True
            st.session_state["user"] = username
            st.success("Login successful!")
            st.rerun()
        else:
            st.error("Invalid username or password")
