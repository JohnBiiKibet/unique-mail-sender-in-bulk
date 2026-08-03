import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import gradio as gr
import pandas as pd

# ==========================================
# CONFIGURATION SETTINGS (HIDDEN BACKEND)
# ==========================================
SMTP_SERVER = "://gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "your_email@gmail.com"
SENDER_PASSWORD = "your_app_password"


def process_uploaded_excel(file_wrapper):
    """Triggers instantly in the background on file drop."""
    if file_wrapper is None:
        return "No file detected."

    file_path = file_wrapper.name

    try:
        df = pd.read_excel(file_path)
    except Exception as e:
        return f"Error loading Excel: {e}"

    # Validation check for headers
    required_columns = ["Email", "Name", "Course"]
    if not all(col in df.columns for col in required_columns):
        return f"Error: Missing columns. Sheet requires: {', '.join(required_columns)}"

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
    except Exception as e:
        return f"Mail authentication failed: {e}"

    success_count = 0

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

        msg = MIMEMultipart()
        msg["From"] = SENDER_EMAIL
        msg["To"] = recipient_email

        # ----------------------------------------------------
        # HIDDEN TEMPLATE LOGIC
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

        try:
            server.send_message(msg)
            success_count += 1
        except Exception:
            pass

    server.quit()
    return f"Completed! Emails dispatched to {success_count} recipients."


# ==========================================
# MINIMALIST LAYOUT DISPLAY
# ==========================================
with gr.Blocks() as demo:
    # Minimal file component with generic labeling
    file_input = gr.File(label="Upload File", file_types=[".xlsx", ".xls"])
    status_output = gr.Textbox(label="Status", interactive=False)

    # Automatic event trigger hook
    file_input.upload(
        fn=process_uploaded_excel, inputs=file_input, outputs=status_output
    )

if __name__ == "__main__":
    demo.launch()
