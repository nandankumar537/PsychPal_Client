import os
import shutil
import subprocess
import sys

def build_executable():
    print("Building PsychPal executable...")
    
    # Create necessary directories
    os.makedirs("dist", exist_ok=True)
    os.makedirs("build", exist_ok=True)
    
    # Ensure server directory exists in the output
    server_dir = os.path.join("dist", "PsychPal", "server")
    os.makedirs(server_dir, exist_ok=True)
    
    # Create data directories that will be needed by the app
    data_dirs = [
        os.path.join(server_dir, "data"),
        os.path.join(server_dir, "data", "models"),
        os.path.join(server_dir, "data", "database"),
        os.path.join(server_dir, "data", "adapters")
    ]
    
    for dir_path in data_dirs:
        os.makedirs(dir_path, exist_ok=True)
    
    # Build the executable using PyInstaller
    command = [
        "pyinstaller",
        "--name=PsychPal",
        "--windowed",
        "--onedir",
        "--clean",
        # "--icon=icon.ico",  # Uncomment and add an icon file if available
        "desktop_app.py"
    ]
    
    subprocess.run(command, check=True)
    
    # Copy necessary server files
    server_files = [
        "server/simplified_app.py",
        "server/mock_services.py"
    ]
    
    for file_path in server_files:
        if os.path.exists(file_path):
            shutil.copy2(file_path, os.path.join("dist", "PsychPal", file_path))
            print(f"Copied {file_path} to dist/PsychPal/{file_path}")
        else:
            print(f"Warning: File {file_path} not found")
    
    # Create a README.txt file
    readme_content = """
PsychPal - Privacy-Focused Mental Health Chatbot
================================================

Thank you for installing PsychPal!

This application runs completely offline on your computer, ensuring your
conversations remain private and secure. All data is stored locally.

Getting Started:
---------------
1. Launch PsychPal.exe
2. Go to the Models tab and download a model
3. Return to the Chat tab to start chatting
4. Your conversations are stored only on your device

Privacy Features:
---------------
- All conversations stay on your computer
- Model runs locally without internet connection
- Optional syncing with privacy-preserving techniques
- No data sharing with external services

For issues or feedback, please visit the project website.
"""
    
    with open(os.path.join("dist", "PsychPal", "README.txt"), "w") as f:
        f.write(readme_content)
    
    print("Executable build complete!")
    print(f"You can find the application in: {os.path.abspath(os.path.join('dist', 'PsychPal'))}")

if __name__ == "__main__":
    build_executable()