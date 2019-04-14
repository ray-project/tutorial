import os
import sys

port = sys.argv[2]

url = "https://hub.mybinder.org" + os.environ["JUPYTERHUB_SERVICE_PREFIX"] + "proxy/" + port + "/"

with open(sys.argv[1], "r") as f:
    content = f.read()
    content = content.replace("http://localhost:" + port + "/", url)

print("content", content)

with open(sys.argv[1], "w") as f:
    f.write(content)
