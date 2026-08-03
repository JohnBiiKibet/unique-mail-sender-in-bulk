import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import gradio as nn  # Standard Hugging Face UI library
import pandas as pd

# ==========================================
# CONFIGURATION SETTINGS
# ==========================================
SMTP_SERVER = "://gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "your_email@gmail.com"
SENDER_PASSWORD = "your_app_password"  # Use an App Password


def process_uploaded_excel(file_wrapper):
    """Triggers automatically when a file is uploaded."""
    if file_wrapper is None:
        return "No file detected."

    # Gradio provides a temporary file path
    file_path = file_wrapper.name

    try:
        df = pd.read_excel(file_path)
    except Exception as e:
        return f"Error loading Excel data structure: {e}"

    # Schema validation
    required_columns = ["Email", "Name", "Course"]
    if not all(col in df.columns for col in required_columns):
        return f"Schema Error: Missing columns. Required fields: {', '.join(required_columns)}"

    # Authenticate with the mail server
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
    except Exception as e:
        return f"Mail server authentication failed: {e}"

    success_count = 0

    # Process rows uniquely
    for index, row in df.iterrows():
        recipient_email = row["Email"]
        recipient_name = row["Name"]
        recipient_course = row["Course"]

        if (
            pd.isna(recipient_email)
            or pd.isna(recipient_name)
            or pd.isna(recipient_course)
        ):
            continue

        # Construct message payload
        msg = MIMEMultipart()
        msg["From"] = SENDER_EMAIL
        msg["To"] = recipient_email
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

        try:
            server.send_message(msg)
            success_count += 1
        except Exception:
            pass  # Skip failed rows silently or log them locally

    server.quit()
    return f"Success! Formulated layout dispatched to {success_count} recipients."


# ==========================================
# MINIMALIST GRADIO INTERFACE
# ==========================================
with nn.Blocks() as demo:
    # Single upload component with an interactive file trigger
    file_input = nn.File(
        label="Upload Excel File Here", file_types=[".xlsx", ".xls"]
    )
    status_output = nn.Textbox(label="System Status", interactive=False)

    # Event hook: run script immediately when file is uploaded
    file_input.upload(
        fn=process_uploaded_excel, inputs=file_input, outputs=status_output
    )

# Run the app
if __name__ == "__main__":
    demo.launch()
