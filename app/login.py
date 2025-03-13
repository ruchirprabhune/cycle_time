import streamlit as st
import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Ensure session state variables exist
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "username" not in st.session_state:
    st.session_state["username"] = ""

# Login page UI
def login_page():
    st.title("Login Page")

    menu = ["Login", "Sign Up"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Login":
        st.subheader("Login")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            try:
                response = supabase.auth.sign_in_with_password({"email": email, "password": password})
                user = response.user
                if user:
                    st.session_state["logged_in"] = True
                    st.session_state["username"] = email
                    st.success(f"Welcome {email}! Redirecting...")
                    st.rerun()
            except Exception as e:
                st.error(f"Login failed: {str(e)}")

    elif choice == "Sign Up":
        st.subheader("Create New Account")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Sign Up"):
            try:
                response = supabase.auth.sign_up({"email": email, "password": password})
                if response:
                    st.success("Account created successfully! Please log in.")
            except Exception as e:
                st.error(f"Sign-up failed: {str(e)}")

# Protect pages - Redirect to login if not authenticated
def require_login():
    if not st.session_state["logged_in"]:
        st.warning("Please log in to access this page.")
        st.stop()

# Run the login page
if __name__ == "__main__":
    login_page()

