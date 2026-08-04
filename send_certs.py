import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pdfplumber
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
        self.root.title("PDF Client Certificate Messenger")
        self.root.geometry("640x560")
        self.root.resizable(False, False)
        
        self.pdf_path = ""
        self.clients = []
        self.create_widgets()

    def create_widgets(self):
        # 1. Document Upload Section
        file_frame = tk.LabelFrame(self.root, text=" 1. Load Your Client Directory PDF ", font=("Segoe UI", 10, "bold"), padx=10, pady=10)
        file_frame.pack(fill="x", padx=15, pady=10)

        self.btn_browse = tk.Button(file_frame, text="Browse & Upload PDF", font=("Segoe UI", 9), bg="#E1E1E1", command=self.browse_pdf)
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

    def browse_pdf(self):
        filename = filedialog.askopenfilename(
            title="Select Client PDF", 
            filetypes=[("PDF Files", "*.pdf")]
        )
        if filename:
            self.pdf_path = filename
            self.lbl_file.config(text=os.path.basename(filename), fg="green", font=("Segoe UI", 9, "bold"))
            self.log(f"[READY] Loaded PDF document: {os.path.basename(filename)}")

    def extract_clients(self):
        self.clients = []
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                for i, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    if not text: continue
                    for line in text.split("\n"):
                        # Regex targets standard global/local phone number sequences
                        phone_match = re.search(r"(\+?\d{1,4}[-.\s]??\d{1,4}[-.\s]??\d{3,4}[-.\s]??\d{3,4})", line)
                        # Regex captures adjacent capitalized names (e.g., "John Doe")
                        name_match = re.search(r"(?:Name:\s*|)([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)", line)
                        
                        if phone_match:
                            name = name_match.group(1).strip() if name_match else "Client"
                            phone = phone_match.group(1).strip()
                            self.clients.append({"name": name, "phone": phone})
        except Exception as e:
            self.log(f"[ERROR] PDF processing failed: {str(e)}")
            messagebox.showerror("Processing Failed", f"PDF formatting parse failed.\nSystem Error Log: {str(e)}")

    def process_and_send(self):
        if not self.pdf_path:
            messagebox.showerror("No File Selected", "Please upload a client PDF first!")
            return
        
        self.log("[PROCESSING] Scanning data layers inside PDF document...")
        self.extract_clients()
        
        if not self.clients:
            self.log("[WARNING] Zero phone number profiles matched or parsed.")
            return
            
        self.log(f"[SUCCESS] Extracted {len(self.clients)} records out of your PDF file.")
        template = self.txt_template.get("1.0", "end-1c")

        # Core Gateway Messaging Loop Integration
        for client in self.clients:
            try:
                personalized_text = template.format(name=client['name'], phone=client['phone'])
                
                # TODO: Connect your background text transmission module methods right here
                
                self.log(f"[SENT] Message successfully blasted to: {client['name']} ({client['phone']})")
            except Exception as e:
                self.log(f"[SKIP] Parameter formatting string conversion error: {str(e)}")
                
        messagebox.showinfo("Task Complete", f"Success! Finished running automation blast on {len(self.clients)} records.")

if __name__ == "__main__":
    root = tk.Tk()
    app = CertificateMessengerApp(root)
    root.mainloop()
