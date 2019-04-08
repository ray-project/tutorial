import os
from subprocess import Popen


def load_jupyter_server_extension(nbapp):
    # """serve the bokeh-app directory with bokeh server"""
    # Popen(["bokeh", "serve", "bokeh-app", "--allow-websocket-origin=*"])
    cwd = os.getcwd()
    with open("/tmp/webserver.log", "w") as f:
        f.write("working directory is " + str(cwd) + "\n")
    os.chdir(os.path.join(cwd, "qreader", "dist"))
    with open("/tmp/webserver.out", "w") as out:
        with open("/tmp/webserver.err", "w") as err:
            Popen(["python", "-m", "http.server"], stdout=out, stderr=err)
