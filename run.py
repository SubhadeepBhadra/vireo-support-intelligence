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
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    app_path = os.path.join(script_dir, "app.py")
    port = 8501
    url = f"http://localhost:{port}"
    
    def open_browser():
        time.sleep(1.5)
        print(f"\n🌐 Opening dashboard in browser: {url}")
        webbrowser.open(url)
        
    import threading
    threading.Thread(target=open_browser, daemon=True).start()
    
    cmd = [
        sys.executable, "-m", "streamlit", "run", app_path,
        "--server.port", str(port),
        "--server.headless", "false"
    ]
    
    try:
        subprocess.run(cmd, cwd=script_dir)
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped.")

if __name__ == '__main__':
    launch()
