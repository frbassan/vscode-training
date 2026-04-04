import urllib.request
import time
import subprocess
import os
import sys

def is_port_in_use(port):
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def find_free_port():
    port = 8501
    while is_port_in_use(port):
        port += 1
    return port

PORT = find_free_port()

def wait_for_server():
    while True:
        try:
            req = urllib.request.urlopen(f'http://localhost:{PORT}', timeout=1)
            if req.status == 200:
                print("Streamlit respondendo corretamente!")
                break
        except Exception:
            time.sleep(0.5)

def get_browser_command():
    # Try Edge (Built-in on Windows 10/11)
    edge_paths = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
    ]
    for p in edge_paths:
         if os.path.exists(p):
             return [p, f'--app=http://localhost:{PORT}']
             
    # Fallback to Chrome
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
    ]
    for p in chrome_paths:
         if os.path.exists(p):
             return [p, f'--app=http://localhost:{PORT}']
    
    # Ultimate Fallback: Just open default browser
    import webbrowser
    return None

if __name__ == '__main__':
    if getattr(sys, 'frozen', False):
        application_path = sys._MEIPASS
    else:
        application_path = os.path.dirname(os.path.abspath(__file__))

    script_path = os.path.join(application_path, 'h5_viewer.py')

    startupinfo = None
    if os.name == 'nt':
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

    process = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", script_path, "--server.port", str(PORT), "--server.headless", "true"],
        cwd=application_path,
        startupinfo=startupinfo,
        env=os.environ.copy()
    )

    try:
        wait_for_server()
        
        browser_cmd = get_browser_command()
        if browser_cmd:
             # Run Edge/Chrome in Native App Mode 
             browser_proc = subprocess.Popen(browser_cmd)
             browser_proc.wait() # Fica segurando a execução enqto a janela está aberta
        else:
             import webbrowser
             webbrowser.open(f'http://localhost:{PORT}')
             while True:
                 time.sleep(1)
                 
    except KeyboardInterrupt:
        pass
    except Exception as e:
        import traceback
        with open('crash_log.txt', 'w') as f:
            f.write(traceback.format_exc())
    finally:
        process.kill()
