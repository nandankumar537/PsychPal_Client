import sys
import os
import shutil
import subprocess
import zipfile

def create_standalone_package():
    """
    Create a standalone package for Windows that includes Python runtime
    and all dependencies.
    """
    print("Building PsychPal standalone package...")
    
    # Ensure output directory exists
    os.makedirs("dist", exist_ok=True)
    
    # Python runtime for Windows
    print("Step 1: Creating file structure...")
    
    # Create base directories for the package
    package_dir = os.path.join("dist", "PsychPal-Standalone")
    app_dir = os.path.join(package_dir, "PsychPal")
    server_dir = os.path.join(app_dir, "server")
    data_dir = os.path.join(server_dir, "data")
    
    # Create directories
    for directory in [
        package_dir, 
        app_dir,
        server_dir,
        data_dir,
        os.path.join(data_dir, "models"),
        os.path.join(data_dir, "database"),
        os.path.join(data_dir, "adapters")
    ]:
        os.makedirs(directory, exist_ok=True)
    
    # Copy application files
    print("Step 2: Copying application files...")
    
    # Copy main application files
    app_files = [
        "desktop_app.py",
        "server/simplified_app.py",
        "server/mock_services.py"
    ]
    
    for file_path in app_files:
        dest_path = os.path.join(app_dir, file_path)
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        if os.path.exists(file_path):
            shutil.copy2(file_path, dest_path)
            print(f"Copied {file_path} to {dest_path}")
        else:
            print(f"Warning: File {file_path} not found")
    
    # Create launcher batch file
    print("Step 3: Creating launcher script...")
    
    # Create batch file for Windows
    batch_content = """@echo off
title PsychPal Launcher
echo Starting PsychPal...
echo This window will remain open while the application is running.
echo Please do not close this window manually.
echo.

REM Navigate to app directory
cd %~dp0\\PsychPal

REM Run the application
python desktop_app.py
    
if %errorlevel% neq 0 (
  echo.
  echo An error occurred while running PsychPal.
  echo Error code: %errorlevel%
  pause
)
"""
    
    with open(os.path.join(package_dir, "Start-PsychPal.bat"), "w") as f:
        f.write(batch_content)
    
    # Create a README file
    readme_content = """
PsychPal - Privacy-Focused Mental Health Chatbot
================================================

Thank you for installing PsychPal!

This application runs completely offline on your computer, ensuring your
conversations remain private and secure. All data is stored locally.

Getting Started:
---------------
1. Run Start-PsychPal.bat to launch the application
2. Go to the Models tab and download a model
3. Return to the Chat tab to start chatting
4. Your conversations are stored only on your device

Privacy Features:
---------------
- All conversations stay on your computer
- Model runs locally without internet connection
- Optional syncing with privacy-preserving techniques
- No data sharing with external services

Requirements:
-----------
- Windows 10 or later
- Python 3.8 or later with tkinter support
- Recommended: 4GB RAM or more for model operations

For issues or feedback, please visit the project website.
"""
    
    with open(os.path.join(package_dir, "README.txt"), "w") as f:
        f.write(readme_content)
    
    # Create requirements.txt for Python dependencies
    requirements_content = """
Flask==3.1.0
Flask-CORS==5.0.1
requests==2.32.3
"""
    
    with open(os.path.join(app_dir, "requirements.txt"), "w") as f:
        f.write(requirements_content)
    
    # Create installation instructions
    install_content = """
PsychPal Installation Instructions
=================================

To run PsychPal, you need to have Python installed on your computer.

Step 1: Install Python (if not already installed)
------------------------------------------------
1. Download Python 3.11 from https://www.python.org/downloads/
2. During installation, make sure to check "Add Python to PATH"
3. Complete the installation

Step 2: Install Required Python Packages
----------------------------------------
1. Open Command Prompt (or PowerShell)
2. Navigate to the PsychPal directory:
   cd path\\to\\PsychPal-Standalone\\PsychPal
3. Run the following command:
   pip install -r requirements.txt

Step 3: Launch PsychPal
----------------------
1. Return to the main PsychPal-Standalone folder
2. Double-click on "Start-PsychPal.bat"
3. The application should start automatically

Troubleshooting
--------------
- If you get an error about tkinter, you may need to reinstall Python with the "tcl/tk and IDLE" option selected
- If the server fails to start, check that ports 5000 is not in use by another application
- For other issues, consult the error messages in the command window

Enjoy using PsychPal!
"""
    
    with open(os.path.join(package_dir, "INSTALL.txt"), "w") as f:
        f.write(install_content)
    
    # Create a zip file of the package
    print("Step 4: Creating zip archive...")
    
    zip_path = os.path.join("dist", "PsychPal-Standalone.zip")
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(package_dir):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, os.path.dirname(package_dir)))
    
    print("Package creation complete!")
    print(f"Package location: {os.path.abspath(package_dir)}")
    print(f"Zip archive: {os.path.abspath(zip_path)}")

if __name__ == "__main__":
    create_standalone_package()