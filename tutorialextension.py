import os
from subprocess import Popen

def load_jupyter_server_extension(nbapp):
    os.chdir("/tmp")
    Popen(["python", "-m", "http.server"])
