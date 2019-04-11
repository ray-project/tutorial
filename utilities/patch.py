import os
import sys

url = "https://hub.mybinder.org" + os.environ["JUPYTERHUB_SERVICE_PREFIX"] + "proxy/5000/"

with open(sys.argv[1], "r") as f:
    content = f.read()
    content = content.replace("http://localhost:5000/", url)

print("content", content)

with open(sys.argv[1], "w") as f:
    f.write(content)
