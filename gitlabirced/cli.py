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

from multiprocessing import Process

def connect_networks(networks):
    """ Connects to all the networks configured in the config file.

    Returns a dictionary using the same keys as in the config file
    containing process and bot object.
    """

    print("conf taken %s " % networks)
    result = {}
    all_bots = []
    all_threads = []
    for net in networks:
        server = networks[net]['url']
        port = networks[net]['port']
        nick = networks[net]['nick']
        channel = '##ironfoot'

        bot = TestBot(channel, nick, server, net, port)
        print("Starting %s" % server)
        thread = Process(target=bot.start)
        thread.start()

        result[net] = {
            'process': thread,
            'bot': bot
        }

    return result

if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover


import irc.bot
import irc.strings
from irc.client import ip_numstr_to_quad, ip_quad_to_numstr


class TestBot(irc.bot.SingleServerIRCBot):
    def __init__(self, channel, nickname, server, net_name, port=6667):
        # TODO pass here the watchers configuration
        irc.bot.SingleServerIRCBot.__init__(
            self, [(server, port)], nickname, nickname)
        self.channel = channel
        self.net_name = net_name

    def on_nicknameinuse(self, c, e):
        c.nick(c.get_nickname() + "_")

    def on_welcome(self, c, e):
        c.join(self.channel)

    def on_privmsg(self, c, e):
        self.do_command(e, e.arguments[0])

    def on_pubmsg(self, c, e):
        print('on pubmsg')
        print('received via', self.net_name)
        print(c, e)
        # TODO: detect the channel, check watchers configuration, and act on consequence
        a = e.arguments[0].split(":", 1)
        if len(a) > 1 and irc.strings.lower(a[0]) == irc.strings.lower(
                self.connection.get_nickname()):
            self.do_command(e, a[1].strip())
        return

    def on_dccmsg(self, c, e):
        # non-chat DCC messages are raw bytes; decode as text
        text = e.arguments[0].decode('utf-8')
        c.privmsg("You said: " + text)

    def on_dccchat(self, c, e):
        if len(e.arguments) != 2:
            return
        args = e.arguments[1].split()
        if len(args) == 4:
            try:
                address = ip_numstr_to_quad(args[2])
                port = int(args[3])
            except ValueError:
                return
            self.dcc_connect(address, port)

    def do_command(self, e, cmd):
        nick = e.source.nick
        c = self.connection

        if cmd == "disconnect":
            self.disconnect()
        elif cmd == "die":
            self.die()
        elif cmd == "stats":
            for chname, chobj in self.channels.items():
                c.notice(nick, "--- Channel statistics ---")
                c.notice(nick, "Channel: " + chname)
                users = sorted(chobj.users())
                c.notice(nick, "Users: " + ", ".join(users))
                opers = sorted(chobj.opers())
                c.notice(nick, "Opers: " + ", ".join(opers))
                voiced = sorted(chobj.voiced())
                c.notice(nick, "Voiced: " + ", ".join(voiced))
        elif cmd == "dcc":
            dcc = self.dcc_listen()
            c.ctcp("DCC", nick, "CHAT chat %s %d" % (
                ip_quad_to_numstr(dcc.localaddress),
                dcc.localport))
        else:
            c.notice(nick, "Not understood: " + cmd)


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
        hooks = self.server.hooks
        token = self.server.token
        bots = self.server.bots
        project = json_params['project']['path_with_namespace']
        for h in hooks:
            if h['project'] == project:
                print('project found!!')
                network = h['network']
                reports = h['reports']
                bot = bots[network]['bot']
                for r in reports:
                    if 'push' in reports[r]:
                        print('sending to %s, in network %s' % (r, network))
                        #bot.privmsg(r, 'pushhhh')
                        bot.connection.privmsg("##ironfoot", "pushh")

            else:
                print("not found", project)
        



