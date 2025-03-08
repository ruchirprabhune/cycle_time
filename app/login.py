import streamlit as st
import hashlib
import json
import os

# File to store user credentials
USER_DATA_FILE = "app/utils/users.json"

# Function to load user credentials
def load_users():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, "r") as file:
            return json.load(file)
    return {}

# Function to save user credentials
def save_users(users):
    with open(USER_DATA_FILE, "w") as file:
        json.dump(users, file, indent=4)

# Function to hash passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Ensure session state variables exist
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "username" not in st.session_state:
    st.session_state["username"] = ""

# Login page UI
def login_page():
    st.title("Login Page")

    users = load_users()

    menu = ["Login", "Sign Up"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Login":
        st.subheader("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            hashed_password = hash_password(password)
            if username in users and users[username] == hashed_password:
                st.session_state["logged_in"] = True
                st.session_state["username"] = username
                st.success(f"Welcome {username}! Redirecting...")
                st.rerun()
            else:
                st.error("Invalid username or password")

    elif choice == "Sign Up":
        st.subheader("Create New Account")
        new_user = st.text_input("New Username")
        new_password = st.text_input("New Password", type="password")

        if st.button("Sign Up"):
            if new_user in users:
                st.warning("Username already exists. Choose a different one.")
            else:
                users[new_user] = hash_password(new_password)
                save_users(users)
                st.success("Account created successfully! Please log in.")

# Protect pages - Redirect to login if not authenticated
def require_login():
    if not st.session_state.get("logged_in", False):
        st.warning("You must log in to access this page.")
        st.stop()
