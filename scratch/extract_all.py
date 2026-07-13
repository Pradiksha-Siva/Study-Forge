import os
import sys

def check_and_install_pypdf():
    try:
        import pypdf
        print("pypdf is already installed.")
    except ImportError:
        print("pypdf not found. Installing...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pypdf"])
        print("pypdf installed successfully.")

def main():
    check_and_install_pypdf()
    
    import pypdf
    pdf_path = r"C:\Users\Pradiksha sivakumar\.gemini\antigravity\brain\fd989da7-3ad1-42a4-a549-b4ad03515e02\media__1782571886682.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"Error: PDF not found at {pdf_path}")
        return
        
    reader = pypdf.PdfReader(pdf_path)
    total_pages = len(reader.pages)
    print(f"PDF loaded successfully. Total pages: {total_pages}")
    
    # Let's inspect page 8 (which is index 7) to check text layout
    page_8_text = reader.pages[7].extract_text()
    print("--- Page 8 (Index 7) Preview ---")
    print(page_8_text[:600])
    
if __name__ == '__main__':
    main()
