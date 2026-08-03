import os
import smtplib
import sys
import tkinter as tk
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from tkinter import filedialog, messagebox
import pandas as pd
import requests

# ==========================================
# SECURE CONFIGURATION VALUES
# ==========================================
SMTP_SERVER = "://gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "your_email@gmail.com"  # Put your email address here
SENDER_PASSWORD = (
    "your_app_password"  # Put your secure 16-digit App Password here
)

AUTOMATION_SUBJECT = "Official Certificate for {Course}"
AUTOMATION_BODY_TEMPLATE = """Dear {Name},

Congratulations! Your custom digital certificate for finishing your {Course} program is successfully compiled and attached below as a PDF document.

Warm regards,
Management"""


class BulkMailApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Bulk Mail System")
        self.root.geometry("400x250")
        self.root.resizable(False, False)

        self.file_path = ""

        # Minimalist UI Elements
        self.label = tk.Label(
            root, text="Bulk Mail & Certificate System", font=("Arial", 14, "bold")
        )
        self.label.pack(pady=20)

        self.upload_btn = tk.Button(
            root,
            text="📁 Upload Excel File",
            command=self.select_file,
            width=25,
            bg="#f0f0f0",
        )
        self.upload_btn.pack(pady=10)

        self.execute_btn = tk.Button(
            root,
            text="Execute Automation Blast",
            command=self.process_emails,
            width=25,
            bg="#28a745",
            fg="white",
            state=tk.DISABLED,
        )
        self.execute_btn.pack(pady=10)

        self.status_label = tk.Label(
            root, text="Status: Waiting for file...", fg="#555"
        )
        self.status_label.pack(pady=10)

    def select_file(self):
        self.file_path = filedialog.askopenfilename(
            filetypes=[("Excel Files", "*.xlsx *.xls"), ("CSV Files", "*.csv")]
        )
        if self.file_path:
            filename = os.path.basename(self.file_path)
            self.upload_btn.config(text=f"📄 {filename}")
            self.execute_btn.config(state=tk.NORMAL)
            self.status_label.config(text="Status: File loaded. Ready to send.")

    def process_emails(self):
        self.execute_btn.config(state=tk.DISABLED, text="Processing...")
        self.root.update()

        try:
            if self.file_path.endswith((".xlsx", ".xls")):
                df = pd.read_excel(self.file_path)
            else:
                df = pd.read_csv(self.file_path)
        except Exception as e:
            messagebox.showerror("Error", f"Could not read spreadsheet: {e}")
            self.reset_ui()
            return

        required_columns = ["Email", "Name", "Course", "Certificate"]
        if not all(col in df.columns for col in required_columns):
            messagebox.showerror(
                "Error",
                f"Missing headers! Ensure sheet columns are exactly:\n{', '.join(required_columns)}",
            )
            self.reset_ui()
            return

        try:
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
        except Exception as e:
            messagebox.showerror("Error", f"Mail server login failed: {e}")
            self.reset_ui()
            return

        success_count = 0

        for index, row in df.iterrows():
            recipient_email = str(row["Email"]).strip()
            recipient_name = str(row["Name"]).strip()
            recipient_course = str(row["Course"]).strip()
            cert_url = str(row["Certificate"]).strip()

            if (
                pd.isna(row["Email"])
                or pd.isna(row["Name"])
                or pd.isna(row["Course"])
                or pd.isna(row["Certificate"])
            ):
                continue

            final_subject = AUTOMATION_SUBJECT.replace(
                "{Course}", recipient_course
            ).replace("{Name}", recipient_name)
            final_body = AUTOMATION_BODY_TEMPLATE.replace(
                "{Course}", recipient_course
            ).replace("{Name}", recipient_name)

            msg = MIMEMultipart()
            msg["From"] = SENDER_EMAIL
            msg["To"] = recipient_email
            msg["Subject"] = final_subject
            msg.attach(MIMEText(final_body, "plain"))

            try:
                response = requests.get(cert_url, timeout=10)
                if response.status_code == 200:
                    file_attachment = MIMEApplication(
                        response.content, _subtype="pdf"
                    )
                    file_attachment.add_header(
                        "Content-Disposition",
                        "attachment",
                        filename=f"{recipient_name.replace(' ', '_')}_Certificate.pdf",
                    )
                    msg.attach(file_attachment)
            except Exception:
                continue

            try:
                server.send_message(msg)
                success_count += 1
            except Exception:
                pass

        server.quit()
        messagebox.showinfo(
            "Success", f"Mail blast complete! Sent to {success_count} clients."
        )
        self.reset_ui()

    def reset_ui(self):
        self.upload_btn.config(text="📁 Upload Excel File")
        self.execute_btn.config(state=tk.DISABLED, text="Execute Automation Blast")
        self.status_label.config(text="Status: Waiting for file...")
        self.file_path = ""


if __name__ == "__main__":
    root = tk.Tk()
    app = BulkMailApp(root)
    root.mainloop()
