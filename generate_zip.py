import os
import sys
import zipfile
import re

def create_submission_zip(roll_no="12345", student_name="Student"):
    # Clean inputs for filename
    clean_roll = re.sub(r'[^a-zA-Z0-9]', '', roll_no)
    clean_name = re.sub(r'[^a-zA-Z0-9]', '', student_name)
    zip_filename = f"{clean_roll}_{clean_name}_Code.zip"

    # Base folder
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Files to exclude from zip (sensitive keys, caches)
    excluded_patterns = [
        ".env",
        ".env.local",
        "__pycache__",
        ".git",
        ".venv",
        "venv",
        ".DS_Store",
        ".zip"
    ]

    print(f"Creating submission zip: {zip_filename}...")
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(current_dir):
            # Skip hidden directories like .git or __pycache__
            dirs[:] = [d for d in dirs if not any(p in d for p in excluded_patterns)]
            
            for file in files:
                if any(p in file for p in excluded_patterns):
                    print(f"  [Skipping sensitive/temporary file]: {file}")
                    continue
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, current_dir)
                zipf.write(file_path, arcname=rel_path)
                print(f"  [Added]: {rel_path}")

    print(f"\nSUCCESS! Created submission file: {zip_filename}")
    print(f"Location: {os.path.abspath(zip_filename)}")

if __name__ == "__main__":
    roll = sys.argv[1] if len(sys.argv) > 1 else input("Enter your Roll Number: ") or "101"
    name = sys.argv[2] if len(sys.argv) > 2 else input("Enter your Name: ") or "Student"
    create_submission_zip(roll, name)
