from http.server import HTTPServer
from http.server import BaseHTTPRequestHandler
import json
import logging


class MyHTTPServer(HTTPServer):

    def __init__(self, token, hooks, bots, *args, **kw):
        HTTPServer.__init__(self, *args, **kw)
        self.token = token
        self.hooks = hooks
        self.bots = bots


class RequestHandler(BaseHTTPRequestHandler):
    """A POST request handler."""

    def do_POST(self):
        hooks = self.server.hooks
        token = self.server.token
        print(hooks)
        logging.info("Hook received")

        # get payload
        header_length = int(self.headers.get('content-length', "0"))
        json_payload = self.rfile.read(header_length)
        print(json_payload)
        json_params = {}
        if len(json_payload) > 0:
            json_params = json.loads(json_payload)

        # get gitlab secret token
        gitlab_token_header = self.headers.get('X-Gitlab-Token')

        # get project homepage
        project = json_params['project']['homepage']

        # get command and token from config file
        gitlab_token = str(token)

        logging.info("Load project '%s'", project)

        # Check if the gitlab token is valid
        print(gitlab_token_header, gitlab_token)
        if gitlab_token_header == gitlab_token:
            logging.info('TOKEN VALID')
            self._handle_push(json_params)
            # TODO: send response on handlers, and send errors when
            # undefined
            self.send_response(200, "OK")
        else:
            logging.error("Not authorized, Gitlab_Token not authorized")
            self.send_response(401, "Gitlab Token not authorized")
        self.end_headers()

    def _handle_push(self, json_params):
        print('handling push')
        hooks = self.server.hooks
        bots = self.server.bots
        project = json_params['project']['path_with_namespace']
        for h in hooks:
            if h['project'] == project:
                print('project found!!')
                network = h['network']
                reports = h['reports']
                branches = h['branches'].split()
                bot = bots[network]['bot']
                branch = json_params['ref'][11:]
                if branch not in branches:
                    continue
                for r in reports:
                    if 'push' in reports[r]:
                        print('sending to %s, in network %s' % (r, network))
                        bot.connection.privmsg(r, "pushh")

            else:
                print("not found", project)
