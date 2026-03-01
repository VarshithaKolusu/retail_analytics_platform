# app.py
import streamlit as st
import requests
import pandas as pd
import altair as alt

# Backend URL
BASE_URL = "http://localhost:5000/api"

# ----------------------
# SESSION STATE SETUP
# ----------------------
if "token" not in st.session_state:
    st.session_state["token"] = None

if "username" not in st.session_state:
    st.session_state["username"] = None

# ----------------------
# LOGIN / SIGNUP FORM
# ----------------------
def auth_form():
    st.title("Retail Dashboard Login / Signup")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Signup"):
            resp = requests.post(f"{BASE_URL}/auth/signup", json={
                "username": username,
                "password": password
            })
            if resp.status_code == 200:
                st.success("Signup successful! Please login.")
            else:
                st.error(resp.json().get("message"))

    with col2:
        if st.button("Login"):
            resp = requests.post(f"{BASE_URL}/auth/login", json={
                "username": username,
                "password": password
            })
            if resp.status_code == 200:
                token = resp.json()["token"]
                st.session_state["token"] = token
                st.session_state["username"] = username
                st.success("Login successful!")
            else:
                st.error(resp.json().get("message"))

# ----------------------
# CSV UPLOAD
# ----------------------
def upload_csv():
    st.subheader("Upload CSV for Dashboard")
    uploaded_file = st.file_uploader("Choose CSV file", type="csv")
    if uploaded_file is not None:
        files = {"file": uploaded_file.getvalue()}
        headers = {"Authorization": f"Bearer {st.session_state['token']}"}

        # Send file to backend
        resp = requests.post(f"{BASE_URL}/data/upload_csv", files={"file": uploaded_file}, headers=headers)
        if resp.status_code == 200:
            st.success("CSV uploaded successfully!")
            st.session_state["metrics"] = resp.json()["metrics"]
        else:
            st.error(resp.json().get("message"))

# ----------------------
# DASHBOARD DISPLAY
# ----------------------
def show_dashboard():
    metrics = st.session_state.get("metrics")
    if not metrics:
        st.info("Upload a CSV to see dashboard metrics.")
        return

    st.subheader("Dashboard KPIs")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Revenue", f"${metrics['totalRevenue']:.2f}")
    col2.metric("Total Profit", f"${metrics['totalProfit']:.2f}")
    col3.metric("Profit Margin", f"{metrics['profitMargin']:.2f}%")

    st.subheader("Top Products")
    top_products = pd.DataFrame(metrics["topProducts"], columns=["Product", "Revenue"])
    chart = alt.Chart(top_products).mark_bar().encode(
        x="Product",
        y="Revenue"
    )
    st.altair_chart(chart, use_container_width=True)

# ----------------------
# MAIN LOGIC
# ----------------------
if st.session_state["token"] is None:
    auth_form()
else:
    st.sidebar.write(f"Logged in as: {st.session_state['username']}")
    upload_csv()
    show_dashboard()