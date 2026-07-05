import socket
import subprocess
import time
import smf

from ..calling import call_bin

class GoEngineManager:
    def __init__(self, port=31337):
        self.port = port
        self.process = None

    def is_running(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.2)
            return s.connect_ex(('127.0.0.1', self.port)) == 0

    def start(self):
        if self.is_running():
            return True

        # Mengambil path absolut biner dari API Storm
        engine_bin = call_bin("sliver-server")
        smf.printd("Booting Go Backend JIT...", level="INFO")
        
        try:
            # Pastikan argumen "daemon" ikut masuk ke dalam list subprocess
            self.process = subprocess.Popen(
                [engine_bin, "daemon"], 
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        except Exception as e:
            smf.printd(f"Failed to spawn engine", e, level="ERROR")
            return False
        
        # Tunggu port terbuka
        for _ in range(15):
            if self.is_running(): 
                smf.printd("Backend initialized successfully.", level="INFO")
                return True
            time.sleep(0.5)
            
        smf.printd("Timeout: Backend failed to bind port.", level="ERROR")
        return False

    def stop(self):
        if self.process:
            self.process.terminate()
            smf.printd("Backend terminated.", level="INFO")
          
