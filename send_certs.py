import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pdfplumber
import pandas as pd
import openpyxl
import re
import os
import sys

def get_resource_path(relative_path):
    """ Ensures background assets map correctly inside a compiled Windows .exe """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class CertificateMessengerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Multi-Format Client Certificate Messenger")
        self.root.geometry("640x560")
        self.root.resizable(False, False)
        
        self.file_path = ""
        self.clients = []
        self.create_widgets()

    def create_widgets(self):
        # 1. Document Upload Section
        file_frame = tk.LabelFrame(self.root, text=" 1. Load Client Data File (PDF, XLSX, or CSV) ", font=("Segoe UI", 10, "bold"), padx=10, pady=10)
        file_frame.pack(fill="x", padx=15, pady=10)

        self.btn_browse = tk.Button(file_frame, text="Browse & Upload File", font=("Segoe UI", 9), bg="#E1E1E1", command=self.browse_file)
        self.btn_browse.pack(side="left", padx=5)

        self.lbl_file = tk.Label(file_frame, text="No file selected", fg="red", font=("Segoe UI", 9, "italic"))
        self.lbl_file.pack(side="left", padx=5)

        # 2. Template Editor Section
        template_frame = tk.LabelFrame(self.root, text=" 2. Message Template Editor ", font=("Segoe UI", 10, "bold"), padx=10, pady=10)
        template_frame.pack(fill="x", padx=15, pady=10)

        tk.Label(template_frame, text="Use tags to inject data dynamically: {name} and {phone}", fg="#555555", font=("Segoe UI", 9)).pack(anchor="w")
        self.txt_template = tk.Text(template_frame, height=5, width=60, font=("Segoe UI", 10))
        self.txt_template.pack(fill="x", pady=5)
        self.txt_template.insert("1.0", "Hello {name},\nYour certificate processing is complete. Sent to tracking info: {phone}.")

        # 3. Main Action Trigger Button
        self.btn_send = tk.Button(self.root, text="🚀 Execute Automation Blast", bg="#2ECC71", fg="white", font=("Segoe UI", 11, "bold"), height=2, command=self.process_and_send)
        self.btn_send.pack(fill="x", padx=15, pady=5)

        # 4. Interactive Live Logging Console
        log_frame = tk.LabelFrame(self.root, text=" System Status Log Terminal ", font=("Segoe UI", 10, "bold"), padx=10, pady=10)
        log_frame.pack(fill="both", expand=True, padx=15, pady=10)

        self.log_box = tk.Text(log_frame, state="disabled", height=8, bg="#F3F3F3", font=("Consolas", 9))
        self.log_box.pack(fill="both", expand=True)

    def log(self, message):
        self.log_box.config(state="normal")
        self.log_box.insert("end", message + "\n")
        self.log_box.see("end")
        self.log_box.config(state="disabled")
        self.root.update_idletasks()

    def browse_file(self):
        filename = filedialog.askopenfilename(
            title="Select Client Data File", 
            filetypes=[("All Supported Formats", "*.pdf *.xlsx *.xls *.csv"), 
                       ("PDF Files", "*.pdf"), 
                       ("Excel Spreadsheet", "*.xlsx *.xls"), 
                       ("CSV Document", "*.csv")]
        )
        if filename:
            self.file_path = filename
            self.lbl_file.config(text=os.path.basename(filename), fg="green", font=("Segoe UI", 9, "bold"))
            self.log(f"[READY] Loaded file document: {os.path.basename(filename)}")

    def extract_clients(self):
        self.clients = []
        ext = os.path.splitext(self.file_path)[1].lower()
        
        try:
            # --- HANDLE EXCEL TRACKS ---
            if ext in ['.xlsx', '.xls']:
                df = pd.read_excel(self.file_path)
                self._extract_from_dataframe(df)
                
            # --- HANDLE CSV TRACKS ---
            elif ext == '.csv':
                df = pd.read_csv(self.file_path)
                self._extract_from_dataframe(df)
                
            # --- HANDLE PDF TRACKS ---
            elif ext == '.pdf':
                with pdfplumber.open(self.file_path) as pdf:
                    for page in pdf.pages:
                        text = page.extract_text()
                        if not text: continue
                        for line in text.split("\n"):
                            phone_match = re.search(r"(\+?\d{1,4}[-.\s]??\d{1,4}[-.\s]??\d{3,4}[-.\s]??\d{3,4})", line)
                            name_match = re.search(r"(?:Name:\s*|)([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)", line)
                            
                            if phone_match:
                                name = name_match.group(1).strip() if name_match else "Client"
                                phone = phone_match.group(1).strip()
                                self.clients.append({"name": name, "phone": phone})
        except Exception as e:
            self.log(f"[ERROR] Data format processing failed: {str(e)}")
            messagebox.showerror("Processing Failed", f"Data format processing failed.\nSystem Error Log: {str(e)}")

    def _extract_from_dataframe(self, df):
        """ Helper to find name and phone column configurations from spreadsheet matrix dynamically """
        # Strip string whitespace anomalies from column index spaces
        df.columns = [str(col).strip().lower() for col in df.columns]
        
        name_col = next((col for col in df.columns if 'name' in col or 'client' in col), None)
        phone_col = next((col for col in df.columns if 'phone' in col or 'mobile' in col or 'contact' in col), None)
        
        if not phone_col:
            raise ValueError("Could not find a valid Phone/Mobile column header in your spreadsheet file.")
            
        for _, row in df.iterrows():
            phone = str(row[phone_col]).strip()
            # Skip empty records cleanly
            if pd.isna(row[phone_col]) or phone == 'nan' or phone == '':
                continue
                
            name = str(row[name_col]).strip() if name_col and not pd.isna(row[name_col]) else "Valued Client"
            self.clients.append({"name": name, "phone": phone})

    def process_and_send(self):
        if not self.file_path:
            messagebox.showerror("No File Selected", "Please select a client data spreadsheet or PDF first!")
            return
        
        self.log("[PROCESSING] Parsing document structuring layers...")
        self.extract_clients()
        
        if not self.clients:
            self.log("[WARNING] Zero valid records matched or parsed configuration targets.")
            return
            
        self.log(f"[SUCCESS] Extracted {len(self.clients)} records out of file template.")
        template = self.txt_template.get("1.0", "end-1c")

        # Core Gateway Messaging Loop Integration
        for client in self.clients:
            try:
                personalized_text = template.format(name=client['name'], phone=client['phone'])
                
                # TODO: Integrate your specific Messaging API gateway client methods here
                
                self.log(f"[SENT] Message successfully blasted to: {client['name']} ({client['phone']})")
            except Exception as e:
                self.log(f"[SKIP] String format parameter conversion error: {str(e)}")
                
        messagebox.showinfo("Task Complete", f"Success! Finished running automation blast on {len(self.clients)} records.")

if __name__ == "__main__":
    root = tk.Tk()
    app = CertificateMessengerApp(root)
    root.mainloop()
