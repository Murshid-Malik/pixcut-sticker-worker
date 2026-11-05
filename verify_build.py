"""Start ComfyUI on CPU and validate the workflow before publishing the image."""
import subprocess
import sys
import time
import urllib.request

process = subprocess.Popen([sys.executable, 'main.py', '--cpu', '--listen', '127.0.0.1', '--port', '8188'], cwd='/comfyui')
try:
    deadline = time.monotonic() + 300
    while True:
        if process.poll() is not None:
            raise RuntimeError('ComfyUI exited during build validation')
        try:
            with urllib.request.urlopen('http://127.0.0.1:8188/object_info', timeout=5):
                break
        except OSError:
            if time.monotonic() > deadline:
                raise RuntimeError('ComfyUI startup timed out')
            time.sleep(2)
    subprocess.run([sys.executable, '/sticker/check_server.py', 'http://127.0.0.1:8188'], check=True)
finally:
    process.terminate()
    try:
        process.wait(timeout=15)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()
