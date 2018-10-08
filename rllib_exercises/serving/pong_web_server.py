import cgi
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import requests
import socketserver
import subprocess
import threading

from ray.rllib.utils.policy_client import PolicyClient


# Check that the required port isn't already in use.
try:
    requests.get('http://localhost:3000')
except:
    pass
else:
    raise Exception('The port 3000 is still in use (perhaps from a previous run of this notebook. '
                    'You will need to kill that process before proceeding, e.g., by running '
                    '"subprocess.call([\'ray\', \'stop\'])" in a new cell and restarting this notebook.')


client = PolicyClient("http://localhost:8900")


def make_handler_class(agent):
    """This function is used to define a custom handler using the policy."""

    class PolicyHandler(BaseHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            BaseHTTPRequestHandler.__init__(self, *args, **kwargs)
            
        def end_headers(self):
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', '*')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            BaseHTTPRequestHandler.end_headers(self)
        
        def do_OPTIONS(self):
            self.send_response(200, 'ok')
            self.end_headers()

        def do_POST(self):
            """This method receives the state of the game and returns an action."""
            length = int(self.headers.get_all('content-length')[0])
            post_body = cgi.parse_qs(self.rfile.read(length), keep_blank_values=1)
            print("Processing request", post_body)
            req = json.loads(list(post_body.keys())[0].decode("utf-8"))
            if "command" in req:
                if req["command"] == "start_episode":
                    resp = client.start_episode(training_enabled=False)
                elif req["command"] == "end_episode":
                    resp = client.end_episode(req["episode_id"], [0] * 8)
                elif req["command"] == "log_returns":
                    if req["playerNo"] == 0:
                        client.log_returns(req["episode_id"], req["reward"])
                    resp = "OK"
                else:
                    raise ValueError("Unknown command")
            else:
                action = client.get_action(req["episode_id"], req["observation"])
                resp = {"output": int(action)}

            self.send_response(200)
            self.send_header('Content-type', 'json')
            self.end_headers()
        
            self.wfile.write(json.dumps(resp).encode('ascii'))

    return PolicyHandler


if __name__ == "__main__":
    handler = make_handler_class(None)
    httpd = HTTPServer(('', 3000), handler)
    print("Starting web server on port 3000.")
    httpd.serve_forever()
