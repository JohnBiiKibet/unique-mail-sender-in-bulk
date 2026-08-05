import subprocess
import sys
import os

def ensure_dependencies():
    """Verifies and automatically installs required PDF processing libraries."""
    try:
        import pdfplumber
    except ImportError:
        print("[INIT] Required library 'pdfplumber' missing. Installing now...")
        try:
            # Silently installs pdfplumber via pip
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pdfplumber"])
            print("[INIT] Installation successful!")
        except Exception as e:
            print(f"[ERROR] Auto-installation failed: {e}")
            print("Please manually run: pip install pdfplumber")
            sys.exit(1)

if __name__ == "__main__":
    # 1. Double check environmental dependencies
    ensure_dependencies()
    
    print("[SYSTEM] Booting PDF Certificate Messenger UI...")
    
    # 2. Import and launch your specific Tkinter application class
    try:
        import tkinter as tk
        # Target your main application script file
        from app import CertificateMessengerApp
        
        root = tk.Tk()
        app = CertificateMessengerApp(root)
        root.mainloop()
        
    except ImportError:
        print("[CRITICAL ERROR] Could not find 'app.py' in this directory.")
        print("Ensure this index file is placed in the same folder as your main application code.")
        input("\nPress Enter to exit...")
