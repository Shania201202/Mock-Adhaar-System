import psycopg2
import os
from datetime import datetime, date

# Database connection details
DB_NAME = os.environ.get("DB_NAME", "ADHAAR SYSTEM")
DB_USER = os.environ.get("DB_USER", "postgres")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "Shania2012*")
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = os.environ.get("DB_PORT", "5432")

def get_db_connection():
    """Establishes and returns a new database connection."""
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    return conn

# --- CRUD Operations for Enrollment Management ---

def create_citizen(aadhaar_number, full_name, dob, gender, address, biometric_id, phone, email):
    """Adds a new citizen record with de-duplication check."""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        # Check for existing biometric ID
        cur.execute("SELECT COUNT(*) FROM residents WHERE biometric_id = %s", (biometric_id,))
        if cur.fetchone()[0] > 0:
            # Log the conflict
            cur.execute(
                """
                INSERT INTO deduplication_conflicts (biometric_id, attempted_aadhaar_number, conflict_date)
                VALUES (%s, %s, %s)
                """,
                (biometric_id, aadhaar_number, datetime.now())
            )
            conn.commit()
            return "De-duplication conflict detected. Record has been flagged for manual review."

        # Insert new record if no conflict
        cur.execute(
            """
            INSERT INTO residents (aadhaar_number, full_name, date_of_birth, gender, current_address, biometric_id, phone_number, email_address, enrollment_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (aadhaar_number, full_name, dob, gender, address, biometric_id, phone, email, date.today())
        )
        conn.commit()
        return "Citizen record created successfully."
    except psycopg2.Error as e:
        conn.rollback()
        return f"Error creating record: {e}"
    finally:
        cur.close()
        conn.close()

def get_all_citizens():
    """Retrieves all citizens from the database."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM residents ORDER BY enrollment_date DESC")
    citizens = cur.fetchall()
    cur.close()
    conn.close()
    return citizens

def update_citizen_details(aadhaar_number, new_address, new_phone, new_email):
    """Updates a citizen's demographic details."""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            UPDATE residents
            SET current_address = %s, phone_number = %s, email_address = %s
            WHERE aadhaar_number = %s
            """,
            (new_address, new_phone, new_email, aadhaar_number)
        )
        conn.commit()
        return "Citizen details updated successfully."
    except psycopg2.Error as e:
        conn.rollback()
        return f"Error updating record: {e}"
    finally:
        cur.close()
        conn.close()

def delete_citizen(aadhaar_number):
    """Deletes a citizen record."""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM residents WHERE aadhaar_number = %s", (aadhaar_number,))
        conn.commit()
        return "Citizen record deleted successfully."
    except psycopg2.Error as e:
        conn.rollback()
        return f"Error deleting record: {e}"
    finally:
        cur.close()
        conn.close()

# --- Authentication and Verification ---

def authenticate(aadhaar_number, submitted_biometric_id):
    """Authenticates a user and logs the attempt."""
    conn = get_db_connection()
    cur = conn.cursor()
    is_successful = False
    failure_reason = None
    try:
        cur.execute("SELECT biometric_id FROM residents WHERE aadhaar_number = %s", (aadhaar_number,))
        result = cur.fetchone()
        
        if result:
            stored_biometric_id = result[0]
            if stored_biometric_id == submitted_biometric_id:
                is_successful = True
            else:
                failure_reason = "Biometric ID mismatch."
        else:
            failure_reason = "Aadhaar number not found."

        # Log the authentication attempt
        cur.execute(
            """
            INSERT INTO authentication_log (aadhaar_number, authentication_date, is_successful, failure_reason)
            VALUES (%s, %s, %s, %s)
            """,
            (aadhaar_number, datetime.now(), is_successful, failure_reason)
        )
        conn.commit()
        
        return is_successful, get_citizen_details(aadhaar_number) if is_successful else None
    except psycopg2.Error as e:
        conn.rollback()
        return False, None
    finally:
        cur.close()
        conn.close()

def get_citizen_details(aadhaar_number):
    """Retrieves a single citizen's details for eKYC simulation."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT full_name, date_of_birth, gender, current_address FROM residents WHERE aadhaar_number = %s", (aadhaar_number,))
    details = cur.fetchone()
    cur.close()
    conn.close()
    return details

# --- Reporting and Analytics ---

def get_business_insights():
    """
    Returns a dictionary of key metrics for the dashboard.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    insights = {}
    try:
        # Total number of enrolled citizens
        cur.execute("SELECT COUNT(*) FROM residents")
        insights["total_enrollments"] = cur.fetchone()[0]

        # Total number of successful and failed authentications
        cur.execute("SELECT COUNT(*) FROM authentication_log WHERE is_successful = TRUE")
        insights["successful_auth"] = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM authentication_log WHERE is_successful = FALSE")
        insights["failed_auth"] = cur.fetchone()[0]
        insights["total_auth_attempts"] = insights["successful_auth"] + insights["failed_auth"]

        # Authentication success rate (AVG)
        cur.execute("SELECT AVG(CASE WHEN is_successful = TRUE THEN 1 ELSE 0 END) FROM authentication_log")
        avg_success_rate = cur.fetchone()[0]
        insights["success_rate"] = round(avg_success_rate * 100, 2) if avg_success_rate is not None else 0

        # Number of de-duplication conflicts
        cur.execute("SELECT COUNT(*) FROM deduplication_conflicts")
        insights["deduplication_conflicts"] = cur.fetchone()[0]

    except psycopg2.Error as e:
        print(f"Error fetching insights: {e}")
    finally:
        cur.close()
        conn.close()
    return insights

def get_auth_logs():
    """Retrieves all authentication log entries."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM authentication_log ORDER BY authentication_date DESC")
    logs = cur.fetchall()
    cur.close()
    conn.close()
    return logs

def get_deduplication_conflicts():
    """Retrieves all de-duplication conflicts."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM deduplication_conflicts ORDER BY conflict_date DESC")
    conflicts = cur.fetchall()
    cur.close()
    conn.close()
    return conflicts