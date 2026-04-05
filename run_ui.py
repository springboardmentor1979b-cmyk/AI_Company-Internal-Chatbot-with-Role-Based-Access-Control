import os
import sys
import subprocess

if __name__ == "__main__":
    # Get current project directory
    project_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Force Streamlit to use the local project directory as the home directory
    # This prevents the [WinError 5] Access is denied to C:\Users\Akhila\.streamlit
    os.environ["USERPROFILE"] = project_dir
    os.environ["HOME"] = project_dir
    
    # Run the frontend application
    print("🚀 Starting Streamlit UI with local permissions bypass...")
    subprocess.run([sys.executable, "-m", "streamlit", "run", "frontend/app.py"])
