import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import os
import sys
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

class CertificateMessengerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Excel Client Certificate Emailer Automation")
        self.root.geometry("680x750")
        self.root.resizable(True, True)
        
        self.excel_path = ""
        self.clients = []
        self.create_widgets()

    def create_widgets(self):
        canvas = tk.Canvas(self.root)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        self.scroll_frame = ttk.Frame(canvas)
        
        self.scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 1. Excel File Upload Section
        file_frame = tk.LabelFrame(self.scroll_frame, text=" 1. Load Your Client Directory Spreadsheet (.xlsx) ", font=("Segoe UI", 10, "bold"), padx=10, pady=10)
        file_frame.pack(fill="x", padx=15, pady=5)

        self.btn_browse = tk.Button(file_frame, text="Browse & Upload Excel", font=("Segoe UI", 9), bg="#E1E1E1", command=self.browse_excel)
        self.btn_browse.pack(side="left", padx=5)

        self.lbl_file = tk.Label(file_frame, text="No Excel file selected", fg="red", font=("Segoe UI", 9, "italic"))
        self.lbl_file.pack(side="left", padx=5)

        # 2. SMTP Mail Server Configurations Dashboard
        smtp_frame = tk.LabelFrame(self.scroll_frame, text=" 2. Sender SMTP Configuration (Background Email Server) ", font=("Segoe UI", 10, "bold"), padx=10, pady=10)
        smtp_frame.pack(fill="x", padx=15, pady=5)

        tk.Label(smtp_frame, text="SMTP Server / Port:", font=("Segoe UI", 9)).grid(row=0, column=0, sticky="w", pady=2)
        self.ent_host = tk.Entry(smtp_frame, font=("Segoe UI", 9))
        self.ent_host.insert(0, "://gmail.com")
        self.ent_host.grid(row=0, column=1, sticky="ew", padx=5)
        
        self.ent_port = tk.Entry(smtp_frame, width=6, font=("Segoe UI", 9))
        self.ent_port.insert(0, "587")
        self.ent_port.grid(row=0, column=2, sticky="w", padx=5)

        tk.Label(smtp_frame, text="Sender Email Account:", font=("Segoe UI", 9)).grid(row=1, column=0, sticky="w", pady=2)
        self.ent_user = tk.Entry(smtp_frame, font=("Segoe UI", 9))
        self.ent_user.grid(row=1, column=1, columnspan=2, sticky="ew", padx=5)

        tk.Label(smtp_frame, text="App Password / Key:", font=("Segoe UI", 9)).grid(row=2, column=0, sticky="w", pady=2)
        self.ent_pass = tk.Entry(smtp_frame, show="*", font=("Segoe UI", 9))
        self.ent_pass.grid(row=2, column=1, columnspan=2, sticky="ew", padx=5)
        
        tk.Label(smtp_frame, text="Email Subject Header:", font=("Segoe UI", 9)).grid(row=3, column=0, sticky="w", pady=2)
        self.ent_subject = tk.Entry(smtp_frame, font=("Segoe UI", 9))
        self.ent_subject.insert(0, "Your Official Certificate Delivery Notification")
        self.ent_subject.grid(row=3, column=1, columnspan=2, sticky="ew", padx=5)

        # 3. Message Template Editor Section
        template_frame = tk.LabelFrame(self.scroll_frame, text=" 3. Message Template Editor ", font=("Segoe UI", 10, "bold"), padx=10, pady=10)
        template_frame.pack(fill="x", padx=15, pady=5)

        tk.Label(template_frame, text="Use tags to inject data dynamically: {name}, {email}, and {certificate}", fg="#555555", font=("Segoe UI", 9)).pack(anchor="w")
        self.txt_template = tk.Text(template_frame, height=5, width=65, font=("Segoe UI", 10))
        self.txt_template.pack(fill="x", pady=5)
        self.txt_template.insert("1.0", "Hello {name},\n\nYour certificate processing is complete. Your verified certificate ({certificate}) has been attached to this email sent to {email}.\n\nBest regards,\nOperations Team")

        # 4. Main Action Trigger Button
        self.btn_send = tk.Button(self.scroll_frame, text="🚀 Execute Automated Row-by-Row Email Blast", bg="#2ECC71", fg="white", font=("Segoe UI", 11, "bold"), height=2, command=self.process_and_send)
        self.btn_send.pack(fill="x", padx=15, pady=10)

        # 5. System Status Log Terminal
        log_frame = tk.LabelFrame(self.scroll_frame, text=" System Status Log Terminal ", font=("Segoe UI", 10, "bold"), padx=10, pady=10)
        log_frame.pack(fill="both", expand=True, padx=15, pady=5)

        self.log_box = tk.Text(log_frame, state="disabled", height=10, bg="#F3F3F3", font=("Consolas", 9))
        self.log_box.pack(fill="both", expand=True)

    def log(self, message):
        self.log_box.config(state="normal")
        self.log_box.insert("end", message + "\n")
        self.log_box.see("end")
        self.log_box.config(state="disabled")
        self.root.update_idletasks()

    def browse_excel(self):
        filename = filedialog.askopenfilename(
            title="Select Client Excel Sheet", 
            filetypes=[("Excel Files", "*.xlsx")]
        )
        if filename:
            self.excel_path = filename
            self.lbl_file.config(text=os.path.basename(filename), fg="green", font=("Segoe UI", 9, "bold"))
            self.log(f"[READY] Target Loaded: {os.path.basename(filename)}")

    def extract_clients_from_excel(self):
        self.clients = []
        try:
            # Reads the Excel file natively
            df = pd.read_excel(self.excel_path)
            
            # Clean sheet column naming styles for matching accuracy
            df.columns = [str(col).strip().lower() for col in df.columns]
            
            # Look up standard header combinations
            name_col = next((c for c in df.columns if 'name' in c), None)
            email_col = next((c for c in df.columns if 'email' in c or 'mail' in c), None)
            cert_col = next((c for c in df.columns if 'cert' in c or 'file' in c or 'path' in c), None)

            if not name_col or not email_col or not cert_col:
                self.log("[ERROR] Spreadsheet missing required 'Name', 'Email', or 'Certificate' columns.")
                messagebox.showerror("Columns Missing", "Please make sure your Excel sheet contains columns named 'Name', 'Email', and 'Certificate'.")
                return False

            for index, row in df.iterrows():
                name = str(row[name_col]).strip()
                email = str(row[email_col]).strip()
                cert = str(row[cert_col]).strip()
                
                # Filter out blank rows
                if email and '@' in email:
                    self.clients.append({"name": name, "email": email, "certificate": cert})
            return True
        except Exception as e:
            self.log(f"[ERROR] Excel processing failed: {str(e)}")
            return False

    def process_and_send(self):
        if not self.excel_path:
            messagebox.showerror("No File Selected", "Please upload a client Excel spreadsheet first!")
            return
        
        if not self.ent_user.get().strip() or not self.ent_pass.get().strip():
            messagebox.showerror("Configuration Missing", "Provide valid SMTP login credentials to authorize background delivery.")
            return

        self.log("[PROCESSING] Parsing row data records from Excel layout...")
        if not self.extract_clients_from_excel() or not self.clients:
            self.log("[WARNING] Zero clients with valid email addresses found.")
            return
            
        self.log(f"[SUCCESS] Extracted {len(self.clients)} records. Authenticating mail stream server connection...")
        
        try {
            server = smtplib.SMTP(self.ent_host.get().strip(), int(self.ent_port.get().strip()))
            server.starttls()
            server.login(self.ent_user.get().strip(), self.ent_pass.get().strip())
        except Exception as e:
            self.log(f"[CRITICAL SMTP ERROR] Server authentication failed: {str(e)}")
            messagebox.showerror("Server Error", f"Could not authenticate SMTP server: {str(e)}")
            return

        template = self.txt_template.get("1.0", "end-1c")
        subject = self.ent_subject.get().strip()
        sender_email = self.ent_user.get().strip()

        success_count = 0
        for client in self.clients:
            try:
                msg = MIMEMultipart()
                msg['From'] = sender_email
                msg['To'] = client['email']
                msg['Subject'] = subject
                
                body = template.format(name=client['name'], email=client['email'], certificate=os.path.basename(client['certificate']))
                msg.attach(MIMEText(body, 'plain'))
                
                # Safe Document Attachment Extraction Logic
                cert_file_path = client['certificate']
                if os.path.exists(cert_file_path):
                    with open(cert_file_path, "rb") as attachment:
                        part = MIMEBase("application", "octet-stream")
                        part.set_payload(attachment.read())
                        encoders.encode_base64(part)
                        part.add_header(
                            "Content-Disposition",
                            f"attachment; filename={os.path.basename(cert_file_path)}",
                        )
                        msg.attach(part)
                else:
                    self.log(f"[FILE WARNING] Attachment file not found for {client['name']}: '{cert_file_path}'. Sending email without attachment.")

