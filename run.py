"""
One-Command Launcher for Vireo Support Intelligence
Starts the Streamlit web dashboard and automatically opens http://localhost:8501 in your default browser.
Automatically detects if the server is already running and opens the browser cleanly.
"""

import subprocess
import webbrowser
import socket
import time
import sys
import os

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def find_available_port(start_port=8501, max_tries=10):
    for p in range(start_port, start_port + max_tries):
        if not is_port_in_use(p):
            return p
    return start_port

def launch():
    print("=" * 60)
    print("⚡ Vireo Support Intelligence Launcher")
    print("=" * 60)
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    app_path = os.path.join(script_dir, "app.py")
    
    # Check if port 8501 is already active
    if is_port_in_use(8501):
        url = "http://localhost:8501"
        print(f"\n✅ Streamlit server is already actively running on {url}!")
        print(f"🌐 Opening dashboard in browser: {url}\n")
        webbrowser.open(url)
        return

    port = find_available_port(8501)
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
