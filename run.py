"""
One-Command Launcher for Vireo Support Intelligence
Starts the Streamlit web dashboard and automatically opens http://localhost:8501 in your default browser.
"""

import subprocess
import webbrowser
import time
import sys
import os

def launch():
    print("=" * 60)
    print("⚡ Launching Vireo Support Intelligence Dashboard...")
    print("=" * 60)
    
    port = 8501
    url = f"http://localhost:{port}"
    
    # Give a brief moment then open browser
    def open_browser():
        time.sleep(1.5)
        print(f"\n🌐 Opening dashboard in browser: {url}")
        webbrowser.open(url)
        
    import threading
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Run Streamlit
    cmd = [
        sys.executable, "-m", "streamlit", "run", "app.py",
        "--server.port", str(port),
        "--server.headless", "false"
    ]
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped.")

if __name__ == '__main__':
    launch()
