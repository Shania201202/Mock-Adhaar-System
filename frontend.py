import streamlit as st
import pandas as pd
from datetime import date
from backend import (
    create_citizen, get_all_citizens, update_citizen_details, delete_citizen,
    authenticate, get_business_insights, get_auth_logs, get_deduplication_conflicts
)

# --- App Layout and Navigation ---
st.set_page_config(
    page_title="Aadhaar Management System",
    page_icon="🇮🇳",
    layout="wide"
)

st.title("🇮🇳 Simplified Aadhaar Management System")
st.markdown("A small-scale application for system administrators to manage enrollments, process authentication requests, and monitor system usage.")
st.markdown("---")

# Use tabs for different sections of the app
tab1, tab2, tab3, tab4 = st.tabs(["Enrollment Management", "Authentication & eKYC", "Dynamic Dashboard", "Admin Logs"])

# --- Enrollment Management Tab ---
with tab1:
    st.header("Enrollment Management")
    st.subheader("Add/Update Citizen Record")
    
    with st.form("citizen_form"):
        aadhaar_number = st.text_input("Aadhaar Number (12 digits)", max_chars=12)
        full_name = st.text_input("Full Name", max_chars=100)
        dob = st.date_input("Date of Birth", value=date.today())
        gender = st.selectbox("Gender", ("Male", "Female", "Other"))
        address = st.text_area("Current Address")
        biometric_id = st.text_input("Unique Biometric ID", max_chars=50)
        phone = st.text_input("Phone Number", max_chars=15)
        email = st.text_input("Email Address", max_chars=100)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            submit_button = st.form_submit_button("Create Record")
        with col2:
            update_button = st.form_submit_button("Update Details (Address/Phone/Email)")
        with col3:
            delete_button = st.form_submit_button("Delete Record")

    if submit_button:
        if len(aadhaar_number) == 12:
            result = create_citizen(aadhaar_number, full_name, dob, gender, address, biometric_id, phone, email)
            st.success(result)
        else:
            st.error("Aadhaar Number must be 12 digits.")

    if update_button:
        if len(aadhaar_number) == 12:
            result = update_citizen_details(aadhaar_number, address, phone, email)
            st.success(result)
        else:
            st.error("Aadhaar Number must be 12 digits.")

    if delete_button:
        if len(aadhaar_number) == 12:
            result = delete_citizen(aadhaar_number)
            st.warning(result)
        else:
            st.error("Aadhaar Number must be 12 digits.")

    st.markdown("---")
    st.subheader("All Enrolled Citizens")
    citizens_data = get_all_citizens()
    if citizens_data:
        df = pd.DataFrame(
            citizens_data,
            columns=["Aadhaar", "Name", "DoB", "Gender", "Address", "Biometric ID", "Phone", "Email", "Enrollment Date"]
        )
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No citizens enrolled yet.")

# --- Authentication & eKYC Tab ---
with tab2:
    st.header("Authentication and Verification")
    st.subheader("Authenticate a Citizen")
    auth_aadhaar = st.text_input("Enter Aadhaar Number to Authenticate")
    auth_biometric = st.text_input("Enter Biometric ID")
    
    if st.button("Authenticate"):
        if auth_aadhaar and auth_biometric:
            success, details = authenticate(auth_aadhaar, auth_biometric)
            if success:
                st.success("Authentication Successful! ✅")
                st.subheader("eKYC Details")
                st.json({
                    "Name": details[0],
                    "Date of Birth": str(details[1]),
                    "Gender": details[2],
                    "Address": details[3]
                })
            else:
                st.error("Authentication Failed. ❌")
                
# --- Dynamic Dashboard Tab ---
with tab3:
    st.header("Dynamic Dashboard")
    st.markdown("Real-time overview of key system metrics.")

    insights = get_business_insights()
    if insights:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Enrollments", insights["total_enrollments"])
            st.metric("Successful Authentications", insights["successful_auth"])
        with col2:
            st.metric("Total Auth Attempts", insights["total_auth_attempts"])
            st.metric("Failed Authentications", insights["failed_auth"])
        with col3:
            st.metric("Auth Success Rate", f"{insights['success_rate']}%")
            st.metric("De-duplication Conflicts", insights["deduplication_conflicts"])

        # Alert for failed authentication
        if insights["failed_auth"] > insights["successful_auth"] * 0.1: # Example alert threshold
            st.warning("🚨 **ALERT:** High number of failed authentication attempts detected. Please investigate potential security issues.")

        # Display charts
        auth_data = pd.DataFrame({
            'Status': ['Successful', 'Failed'],
            'Count': [insights["successful_auth"], insights["failed_auth"]]
        })
        st.bar_chart(auth_data.set_index('Status'))

    else:
        st.error("Could not load dashboard insights.")

# --- Admin Logs Tab ---
with tab4:
    st.header("Admin Logs & Reports")

    st.subheader("Authentication Log")
    auth_logs = get_auth_logs()
    if auth_logs:
        df_auth = pd.DataFrame(
            auth_logs,
            columns=["Log ID", "Aadhaar Number", "Date & Time", "Successful", "IP Address", "Reason"]
        )
        st.dataframe(df_auth, use_container_width=True)
    else:
        st.info("No authentication logs available.")

    st.subheader("De-duplication Conflict Report")
    conflict_logs = get_deduplication_conflicts()
    if conflict_logs:
        df_conflict = pd.DataFrame(
            conflict_logs,
            columns=["Conflict ID", "Biometric ID", "Attempted Aadhaar", "Date & Time", "Status"]
        )
        st.dataframe(df_conflict, use_container_width=True)
    else:
        st.info("No de-duplication conflicts recorded.")