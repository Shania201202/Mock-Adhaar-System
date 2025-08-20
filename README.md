# Mock-Adhaar-System
Markdown

# 🇮🇳 Simplified Aadhaar Management System

This is a small-scale, open-source application designed to simulate a simplified Aadhaar management system. It allows a system administrator to manage citizen enrollments, process authentication requests, and monitor key system metrics through a dynamic dashboard. The application is built with Python, using the Streamlit library for the front end and a PostgreSQL database for the back end.

---

## 🚀 Features

* **Enrollment Management**: Add, update, and delete citizen records, including demographic and unique biometric information.
* **De-duplication Check**: Automatically flags new enrollments with existing biometric IDs, logging a conflict for manual review.
* **Authentication & eKYC**: Process authentication requests by matching an Aadhaar ID with a submitted biometric ID, simulating an eKYC function on successful verification.
* **Dynamic Dashboard**: Provides a real-time overview of key metrics, including total enrollments, authentication success rates, and de-duplication conflicts.
* **Comprehensive Logs**: Generates reports on all authentication attempts and de-duplication conflicts.
* **Alerts**: Notifies administrators of a high number of failed authentication attempts, indicating potential security issues.

---

## 🛠️ Technologies Used

* **Python**: The core programming language for both the frontend and backend.
* **Streamlit**: A powerful and intuitive library used to build the interactive web application interface.
* **PostgreSQL**: A robust and reliable relational database system used to store all application data.
* **Psycopg2**: A PostgreSQL adapter for Python, used to connect the application to the database.

---

## 📦 Getting Started

### Prerequisites

* **Python 3.7+**
* **PostgreSQL** installed and running on your system.

### 1. Database Setup

First, you need to create the database and tables. Open your terminal and access the PostgreSQL command-line interface (`psql`).

```bash
psql -U postgres
Then, copy and paste the following SQL commands to create the database and all necessary tables.

SQL

-- Create the database
CREATE DATABASE aadhaar_management_db;

-- Connect to the new database
\c aadhaar_management_db;

-- Create the 'residents' table
CREATE TABLE residents (
    aadhaar_number VARCHAR(12) PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    date_of_birth DATE NOT NULL,
    gender VARCHAR(10) NOT NULL,
    current_address TEXT,
    biometric_id VARCHAR(50) UNIQUE NOT NULL,
    phone_number VARCHAR(15),
    email_address VARCHAR(100),
    enrollment_date DATE NOT NULL
);

-- Create the 'authentication_log' table
CREATE TABLE authentication_log (
    log_id SERIAL PRIMARY KEY,
    aadhaar_number VARCHAR(12) REFERENCES residents(aadhaar_number),
    authentication_date TIMESTAMP NOT NULL,
    is_successful BOOLEAN NOT NULL,
    failure_reason TEXT
);

-- Create a table for de-duplication conflicts
CREATE TABLE deduplication_conflicts (
    conflict_id SERIAL PRIMARY KEY,
    biometric_id VARCHAR(50) UNIQUE,
    attempted_aadhaar_number VARCHAR(12),
    conflict_date TIMESTAMP NOT NULL,
    status VARCHAR(20) DEFAULT 'Pending'
);
2. Install Python Libraries
Install all required Python libraries using pip.

Bash

pip install streamlit psycopg2-binary
3. Configure Database Credentials
The application connects to the database using credentials. You must set your PostgreSQL password for the application to work. You can do this by setting an environment variable or by directly editing the backend.py file.

Option A: Environment Variable (Recommended)
Open your terminal and set the DB_PASSWORD variable.

macOS/Linux:

Bash

export DB_PASSWORD='your_postgres_password'
Windows:

Bash

set DB_PASSWORD=your_postgres_password
Option B: Edit the File
Open backend.py and replace "your_password" with your actual PostgreSQL password.

Python

# In backend.py
DB_PASSWORD = os.environ.get("DB_PASSWORD", "your_postgres_password")
4. Run the Application
Navigate to the directory containing the frontend.py and backend.py files in your terminal and run the Streamlit application.

Bash

streamlit run frontend.py
Your browser will automatically open the application.

📂 File Structure
The project is organized into two main files to promote code readability and maintainability based on CRUD principles.

frontend.py: Contains the Streamlit code for the user interface and all forms. It calls functions from backend.py.

backend.py: Contains all the database interaction logic, including functions for CRUD operations and business insights.
