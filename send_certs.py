import io
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pandas as pd
import streamlit as st

# --- Page Layout Configuration ---
st.set_page_config(page_title="Certificate Automation", layout="centered")
st.title("🎓 Automated Certificate Emailer")
st.write("Upload your formatted Excel file below to dispatch certificates.")

# --- Email Credentials (Loaded Securely from Hugging Face Settings) ---
SMTP_SERVER = "://gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = os.environ.get("SENDER_EMAIL")
SENDER_PASSWORD = os.environ.get("SENDER_PASSWORD")

# --- UI Warning if secrets are missing ---
if not SENDER_EMAIL or not SENDER_PASSWORD:
    st.error(
        "⚠️ Configuration Missing! Please set SENDER_EMAIL and SENDER_PASSWORD secrets in Space settings."
    )

# --- 1. File Upload UI ---
uploaded_file = st.file_uploader(
    "Drag and drop your students Excel file here", type=["xlsx", "xls"]
)

if uploaded_file is not None:
    try:
        # Read the file directly out of Hugging Face's container memory
        df = pd.read_excel(io.BytesIO(uploaded_file.read()))

        # Check for mandatory data headers
        required_columns = [
            "First_Name",
            "Last_Name",
            "Email",
            "Course",
            "Passed",
            "Certificate_URL",
        ]
        missing_cols = [col for col in required_columns if col not in df.columns]

        if missing_cols:
            st.error(
                f"❌ Invalid format layout. Missing expected columns: {missing_cols}"
            )
        else:
            # Preview loaded entries
            st.success("✅ Excel File Layout Verified!")
            st.write("### Data Preview (Showing top 5 rows)")
            st.dataframe(df.head(5))

            # Filter for rows where passed is explicitly True
            passed_df = df[
                (df["Passed"].astype(str).str.strip().str.lower() == "true")
                & (df["Email"].notna())
                & (df["Certificate_URL"].notna())
            ]

            st.metric(
                label="Total Passing Students Found", value=len(passed_df)
            )

            # --- 2. Dispatch Button Action ---
            if st.button("🚀 Begin Email Dispatch", type="primary"):
                if not SENDER_EMAIL or not SENDER_PASSWORD:
                    st.error("Cannot proceed without environment secrets.")
                else:
                    progress_text = st.empty()
                    progress_bar = st.progress(0)

                    try:
                        # Establish a single pipeline session to prevent server spam
                        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
                        server.starttls()
                        server.login(SENDER_EMAIL, SENDER_PASSWORD)

                        total = len(passed_df)
                        for idx, (index, row) in enumerate(
                            passed_df.iterrows()
                        ):
                            # Craft email message payload
                            msg = MIMEMultipart()
                            msg["From"] = SENDER_EMAIL
                            msg["To"] = row["Email"]
                            msg["Subject"] = (
                                f"Congratulations! Your Certificate for {row['Course']}"
                            )

                            body = f"""
                            <html>
                                <body>
                                    <p>Dear {row['First_Name']},</p>
                                    <p>Congratulations on passing the course <strong>{row['Course']}</strong>!</p>
                                    <p>Access your official digital certificate here:</p>
                                    <p><a href="{row['Certificate_URL']}" style="padding: 10px 20px; background-color: #4CAF50; color: white; text-decoration: none; border-radius: 5px;">View My Certificate</a></p>
                                    <br>
                                    <p>Best regards,<br>Learning Administration</p>
                                </body>
                            </html>
                            """
                            msg.attach(MIMEText(body, "html"))

                            # Execute send action
                            server.sendmail(
                                SENDER_EMAIL, row["Email"], msg.as_string()
                            )

                            # Update Streamlit visual feedback indicators
                            progress_text.text(
                                f"Sending to {row['Email']} ({idx+1}/{total})..."
                            )
                            progress_bar.progress((idx + 1) / total)

                        server.quit()
                        st.balloons()
                        st.success("🎉 All certificate emails sent successfully!")

                    except Exception as email_err:
                        st.error(f"Mail system error occurred: {email_err}")

    except Exception as e:
        st.error(f"Error handling file execution: {e}")
