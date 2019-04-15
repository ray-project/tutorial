import os
from subprocess import Popen

def load_jupyter_server_extension(nbapp):
    cwd = os.getcwd()
    # The following will replace "localhost" with the right binder url
    Popen("python utilities/patch.py examples/news_recommendation_serving.ipynb 9000", shell=True)
    Popen("python utilities/patch.py exercises/exercise01-Introduction.ipynb 8000", shell=True)
    os.chdir(os.path.join(cwd, "qreader", "dist"))
    Popen("python ../../utilities/patch.py static/js/app.*.js 5000", shell=True)

    Popen(["python", "-m", "http.server", "9000"])
    os.chdir("/tmp")
    Popen(["python", "-m", "http.server"])
