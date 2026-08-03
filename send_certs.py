import os
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import gradio as gr
import pandas as pd

# ==========================================
# BACKEND SETTINGS (HIDDEN FROM DISPLAY)
# ==========================================
# Input your direct SMTP email configuration details here
SMTP_SERVER = "://gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "your_email@gmail.com"
SENDER_PASSWORD = "your_app_password"  # Use a secure App Password, not a standard login pass

AUTOMATION_SUBJECT = "Official Certificate for {Course}"
AUTOMATION_BODY_TEMPLATE = """Dear {Name},

Congratulations! Your custom digital certificate for finishing your {Course} program is successfully compiled and attached below as a PDF document.

Warm regards,
Management"""


def run_bulk_pipeline(file_obj):
    """Parses Excel dataset and directly fires emails via secure native SMTP channels."""
    if file_obj is None:
        return "Please upload an Excel workbook sheet before running execution."

    try:
        # Load the uploaded file data stream directly
        df = pd.read_excel(file_obj.name)
    except Exception as e:
        return f"File parser crash structural check: {str(e)}"

    # Enforce database schema parameters case-sensitively
    required_columns = ["Email", "Name", "Course"]
    if not all(col in df.columns for col in required_columns):
        return f"Database Schema Mismatch! Missing fields. Ensure columns are explicitly labeled: {', '.join(required_columns)}"

    # Initialize connection tracking with direct mail network server
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
    except Exception as e:
        return (
            f"Direct network authentication failed. Verify SMTP keys: {str(e)}"
        )

    success_count = 0

    for index, row in df.iterrows():
        recipient_email = str(row["Email"]).strip()
        recipient_name = str(row["Name"]).strip()
        recipient_course = str(row["Course"]).strip()

        # Safely skip corrupted or empty row profiles
        if (
            pd.isna(row["Email"])
            or pd.isna(row["Name"])
            or pd.isna(row["Course"])
        ):
            continue

        # Format layout templates dynamically
        final_subject = AUTOMATION_SUBJECT.replace(
            "{Course}", recipient_course
        ).replace("{Name}", recipient_name)
        final_body = AUTOMATION_BODY_TEMPLATE.replace(
            "{Course}", recipient_course
        ).replace("{Name}", recipient_name)

        # Build message container
        msg = MIMEMultipart()
        msg["From"] = SENDER_EMAIL
        msg["To"] = recipient_email
        msg["Subject"] = final_subject
        msg.attach(MIMEText(final_body, "plain"))

        # ----------------------------------------------------------------
        # SIMULATED PDF CERTIFICATE PIPELINE (OR ATTACH PRE-CREATED LOCAL FILES)
        # ----------------------------------------------------------------
        # If your local space container already stores files dynamically matching names:
        pdf_path = f"certificates/{recipient_name}.pdf"

        if os.path.exists(pdf_path):
            try:
                with open(pdf_path, "rb") as f:
                    file_attachment = MIMEApplication(
                        f.read(), _subtype="pdf"
                    )
                    file_attachment.add_header(
                        "Content-Disposition",
                        "attachment",
                        filename=f"{recipient_name}_Certificate.pdf",
                    )
                    msg.attach(file_attachment)
            except Exception as e:
                print(f"Skipping attachment index loop block: {e}")

        # Dispatch real network transmission package
        try:
            server.send_message(msg)
            success_count += 1
        except Exception as e:
            print(f"Failed handling record transaction row index {index}: {e}")

    server.quit()
    return f"Automation pipeline sequence finished! Dispatched to {success_count} unique recipients."


# ==========================================
# MINIMALIST HUGGING FACE UI ENGINE
# ==========================================
# Custom CSS stylesheet variables used to strip headers and mimic styling
custom_theme_css = """
footer {visibility: hidden !important;}
#component-0 {max-width: 400px; margin: 100px auto !important; text-align: center;}
"""

with gr.Blocks(css=custom_theme_css, title="Bulk Mail System") as demo:

    # File input box matching original clean layout aesthetics
    excel_picker = gr.File(
        label="Choose File", file_types=[".xlsx", ".xls", ".csv"]
    )

    # Action execution blast button
    execute_btn = gr.Button(
        "Execute Automation Blast", variant="primary", size="lg"
    )

    # Simple feedback line block to monitor execution output logs
    log_status = gr.Textbox(label="Status output", interactive=False)

    # Wire button to trigger the execution process
    execute_btn.click(
        fn=run_bulk_pipeline, inputs=excel_picker, outputs=log_status
    )

if __name__ == "__main__":
    demo.launch()
