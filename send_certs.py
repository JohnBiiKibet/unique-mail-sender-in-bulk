import email.utils
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pandas as pd

# --- CONFIGURATION SETTINGS ---
SMTP_SERVER = "://gmail.com"  # e.g., ://gmail.com for Gmail
SMTP_PORT = 587  # Standard TLS port
SENDER_EMAIL = "your.email@gmail.com"
SENDER_PASSWORD = "your_app_password"  # Use an App Password, NOT your regular password


def send_certificates(excel_file_path):
    try:
        # 1. Load the Excel data
        df = pd.read_excel(excel_file_path)

        # 2. Filter: Keep only students who passed and have a valid email/certificate
        # This handles cases where 'Passed' is a string ("True") or boolean (True)
        passed_students = df[
            (df["Passed"].astype(str).str.strip().str.lower() == "true")
            & (df["Email"].notna())
            & (df["Certificate_URL"].notna())
        ]

        print(f"Found {len(passed_students)} passing students to email.\n")

        # 3. Connect to the secure email server
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()  # Upgrade the connection to secure encryption
        server.login(SENDER_EMAIL, SENDER_PASSWORD)

        # 4. Loop through each student and send the email
        for index, row in passed_students.iterrows():
            first_name = row["First_Name"]
            last_name = row["Last_Name"]
            recipient_email = row["Email"]
            course_name = row["Course"]
            cert_url = row["Certificate_URL"]

            # Create email structure
            msg = MIMEMultipart()
            msg["From"] = email.utils.formataddr(
                ("Course Administration", SENDER_EMAIL)
            )
            msg["To"] = email.utils.formataddr(
                (f"{first_name} {last_name}", recipient_email)
            )
            msg["Subject"] = f"Congratulations! Your Certificate for {course_name}"

            # Email Body text (HTML supported)
            body = f"""
            <html>
                <body>
                    <p>Dear {first_name},</p>
                    <p>Congratulations on passing the course <strong>{course_name}</strong>!</p>
                    <p>Your hard work has paid off. You can access and download your official digital certificate using the link below:</p>
                    <p><a href="{cert_url}" style="padding: 10px 20px; background-color: #4CAF50; color: white; text-decoration: none; border-radius: 5px;">View My Certificate</a></p>
                    <br>
                    <p>Best regards,<br>Your Learning Team</p>
                </body>
            </html>
            """
            msg.attach(MIMEText(body, "html"))

            # Send the email
            server.sendmail(SENDER_EMAIL, recipient_email, msg.as_string())
            print(f"Successfully sent certificate email to: {recipient_email}")

        # Clean up connection
        server.quit()
        print("\nAll emails processed completely.")

    except Exception as e:
        print(f"An error occurred during execution: {e}")


# Run the script with your saved Excel file
# send_certificates("students.xlsx")
