# -*- coding: utf-8 -*-

"""Console script for gitlabirced."""
import signal
import sys
import click

from http.server import HTTPServer
from http.server import BaseHTTPRequestHandler
import json

import irc
import yaml

import logging

from .irc_client import MyIRCClient, connect_networks

@click.command()
@click.argument('config-file', nargs=1)
def main(config_file):
    """Console script for gitlabirced."""
    click.echo(config_file)

    try:
        with open(config_file, 'r') as stream:
            config = yaml.load(stream)
            print("Configuration loaded %s" % config)
    except yaml.YAMLError as exc:
        print(exc)
    except IOError:
        print("File %s not found" % config_file)

    bots = []
    all_bots = connect_networks(config['networks'])

    hooks = parse_hooks(config['hooks'])
    token = config['token']

    def run_server(addr, port):
        """Start a HTTPServer which waits for requests."""
        httpd = MyHTTPServer(token, hooks, all_bots, (addr, port), RequestHandler)
        httpd.serve_forever()
        print('serving')

    print('going to execute server')
    run_server('0.0.0.0', 1337)

    def signal_handler(sig, frame):
        print('You pressed Ctrl+C!')
        for b in all_bots:
            all_bots[b]['bot'].reactor.disconnect_all()
            all_bots[b]['process'].terminate()
        click.Abort()
        sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler)

    print('Press Ctrl+C')

    return 0


def parse_hooks(hooks):
    print('parsing hooks')
    print(hooks)
    return hooks

if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover

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
        bots = self.server.bots
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

        try:
            # get command and token from config file
            gitlab_token = str(token)

            logging.info("Load project '%s' and run command '%s'", project)
        except KeyError as err:
            self.send_response(500, "KeyError")
            logging.error("Project '%s' not found in %s", project, args.cfg)
            self.end_headers()
            return

        # Check if the gitlab token is valid
        print(gitlab_token_header, gitlab_token)
        if gitlab_token_header == gitlab_token:
            logging.info('TOKEN VALID')
            self._handle_push(json_params)
            self.send_response(200, "OK")
        else:
            logging.error("Not authorized, Gitlab_Token not authorized")
            self.send_response(401, "Gitlab Token not authorized")
        self.end_headers()
    
    def _handle_push(self, json_params):
        print('handling push')
        hooks = self.server.hooks
        token = self.server.token
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
                        #bot.privmsg(r, 'pushhhh')
                        bot.connection.privmsg(r, "pushh")

            else:
                print("not found", project)
        



