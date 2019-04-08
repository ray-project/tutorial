import os
from subprocess import Popen


def load_jupyter_server_extension(nbapp):
    # """serve the bokeh-app directory with bokeh server"""
    # Popen(["bokeh", "serve", "bokeh-app", "--allow-websocket-origin=*"])
    cwd = os.getcwd()
    with open("/tmp/webserver.log", "w") as f:
        f.write("working directory is " + str(cwd) + "\n")
    Popen(["npm", "run", "dev"])
