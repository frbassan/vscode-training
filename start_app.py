import sys
import streamlit.web.cli as stcli
import os
import subprocess
import urllib.request
import time
from threading import Thread

def start_webview():
    time.sleep(1) # wait for server config
    port = 8501
    
    # Wait for server
    while True:
        try:
            req = urllib.request.urlopen(f'http://localhost:{port}', timeout=1)
            if req.status == 200:
                break
        except:
            time.sleep(0.5)
            
    # Try Edge (Built-in on Windows 10/11)
    edge_paths = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
    ]
    for p in edge_paths:
         if os.path.exists(p):
             subprocess.Popen([p, f'--app=http://localhost:{port}'])
             return
             
    # Fallback to Chrome
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
    ]
    for p in chrome_paths:
         if os.path.exists(p):
             subprocess.Popen([p, f'--app=http://localhost:{port}'])
             return

if __name__ == '__main__':
    Thread(target=start_webview, daemon=True).start()
    
    application_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    script_path = os.path.join(application_path, 'h5_viewer.py')
    
    sys.argv = ["streamlit", "run", script_path, "--server.headless", "true"]
    sys.exit(stcli.main())
