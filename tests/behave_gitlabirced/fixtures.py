from behave import fixture
import http.server
import irc.server
import logging
import threading
import time

from gitlabirced.cli import Client, _configure_logging


logger = logging.getLogger(__name__)


class CustomHandler(irc.server.IRCClient):
    """
    Immediately disconnect the client after connecting
    """
    def _store_log(self, log):
        logger.info('IRCSERVER received - %s' % log)
        self.server.log.append(log)

    def _store_message(self, target, message):
        messages = self.server.messages.get(target, [])
        messages.append(message)
        self.server.messages[target] = messages

    def handle_pass(self, the_password):
        log = 'PASS %s' % the_password
        self._store_log(log)

    def handle_privmsg(self, message):
        message_split = message.split(' ')
        target = message_split[0]
        only_message = ' '.join(message_split[1:])

        log = 'PRIVMSG %s' % message
        self._store_log(log)
        self._store_message(target, only_message)
        super(CustomHandler, self).handle_privmsg(message)


class LoggedIRCServer(irc.server.IRCServer):
    def __init__(self, *args, **kwargs):
        self.clean_messages()
        super().__init__(*args, **kwargs)

    def clean_messages(self):
        logger.info('IRCSERVER cleaning logs')
        self.log = []
        self.messages = {}


class GitlabRequestHandler(http.server.BaseHTTPRequestHandler):
    """A POST request handler."""
    def do_GET(self):
        logger.info('GITLAB received GET "%s"' % self.path)
        # Subset of real answer, for more information see following example:
        # https://gitlab.com/api/v4/projects/baserock%2Fdefinitions/issues/12
        safe_path = self.path
        fake_title = safe_path[1:].replace('/', ' ').title()
        fake_url = "http://fakegitlab.com{path}".format(path=safe_path)
        response_tmpl = '{"title":"%s", "web_url":"%s"}'
        response = response_tmpl % (fake_title, fake_url)

        self.send_response(200, "OK")
        self.end_headers()
        self.wfile.write(response.encode())


@fixture
def gitlab_api(context, port=0):
    addr = '127.0.0.1'
    api_server = http.server.HTTPServer((addr, port), GitlabRequestHandler)
    api_server.host, api_server.port = api_server.socket.getsockname()
    logger.info('FIXTURE gitlab_api starting (port %s)' % api_server.port)
    thread = threading.Thread(target=api_server.serve_forever)
    thread.start()
    yield api_server
    logger.info('FIXTURE gitlab_api shutting down (port %s)' % api_server.port)
    api_server.shutdown()


@fixture
def irc_server(context, port=0):
    bind_address = '127.0.0.1', port
    server = LoggedIRCServer(bind_address, CustomHandler)
    server.host, server.port = server.socket.getsockname()
    logger.info('FIXTURE irc_server starting (port %s)' % server.port)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.start()
    yield server
    logger.info('FIXTURE irc_server shutting down (port %s)' % server.port)
    server.shutdown()
    server_thread.join()
    logger.info('FIXTURE irc_server log %s' % server.log)


@fixture
def run_bot(context, config_file):
    logger.info('FIXTURE run_bot starting')
    _configure_logging(4)
    bot = Client(config_file)
    bot.start()
    # Wait a bit for bot to connect to IRC servers
    time.sleep(0.1)
    context.bot_port = bot.port_used
    yield bot
    logger.info('FIXTURE run_bot stopping')
    bot.stop()
