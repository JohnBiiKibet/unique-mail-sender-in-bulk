import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pandas as pd

# ==========================================
# CONFIGURATION SETTINGS
# ==========================================
# Email Server Authentication (Direct SMTP)
SMTP_SERVER = "://gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "your_email@gmail.com"
SENDER_PASSWORD = "your_app_password"  # Use your specific App Password

# Excel Settings
EXCEL_FILE = "recipients.xlsx"


def process_and_send_emails():
    """Reads the Excel file and dispatches hardcoded template emails."""
    print("Initializing offline email dispatch sequence...")

    # Validate Excel source
    if not os.path.exists(EXCEL_FILE):
        print(f"Critical Error: Source file '{EXCEL_FILE}' not found.")
        return

    try:
        df = pd.read_excel(EXCEL_FILE)
    except Exception as e:
        print(f"Error loading Excel data structure: {e}")
        return

    # Enforce schema validation
    required_columns = ["Email", "Name", "Course"]
    if not all(col in df.columns for col in required_columns):
        print(
            f"Schema Error: Missing columns. Required fields: {', '.join(required_columns)}"
        )
        return

    # Authenticate with the direct mail server
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
    except Exception as e:
        print(f"Mail server authentication failed: {e}")
        return

    # Process rows uniquely
    for index, row in df.iterrows():
        recipient_email = row["Email"]
        recipient_name = row["Name"]
        recipient_course = row["Course"]

        # Handle null anomalies safely
        if (
            pd.isna(recipient_email)
            or pd.isna(recipient_name)
            or pd.isna(recipient_course)
        ):
            print(f"Skipping index line {index + 1}: Contains empty values.")
            continue

        # Construct message payload
        msg = MIMEMultipart()
        msg["From"] = SENDER_EMAIL
        msg["To"] = recipient_email

        # ----------------------------------------------------
        # HARDCODED TEMPLATE LAYOUT
        # ----------------------------------------------------
        msg["Subject"] = f"Official Certificate for {recipient_course}"

        body = (
            f"Dear {recipient_name},\n\n"
            f"Congratulations! Your custom digital certificate for finishing your "
            f"{recipient_course} program is successfully compiled and attached below "
            f"as a PDF document.\n\n"
            f"Warm regards,\n"
            f"Management"
        )
        msg.attach(MIMEText(body, "plain"))
        # ----------------------------------------------------

        # Dispatch
        try:
            server.send_message(msg)
            print(
                f"[{index + 1}] Successfully sent to: {recipient_email} ({recipient_course})"
            )
        except Exception as e:
            print(f"Failed transmission to {recipient_email}: {e}")

    server.quit()
    print("Process complete. All unique rows parsed.")


if __name__ == "__main__":
    # Runs automatically when executing the main file locally
    process_and_send_emails()
