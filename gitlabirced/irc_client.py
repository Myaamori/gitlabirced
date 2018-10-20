import irc.strings
import irc.client
import irc.bot

import logging
import threading
import time
import re
import requests
import urllib

irc_client_logger = logging.getLogger(__name__)


class MyIRCClient(irc.bot.SingleServerIRCBot):
    def __init__(self, channels, nickname, server, net_name, port=6667,
                 watchers=None, nickpass=None, auth_type=None):

        saslpass = nickpass
        if auth_type and auth_type.lower() != 'sasl':
            saslpass = None
        spec = irc.bot.ServerSpec(server, port, saslpass)
        irc.bot.SingleServerIRCBot.__init__(
            self, [spec], nickname, nickname)

        # Monkey patch process_forever with a custom loop that we can stop
        def process_forever(timeout=0.2):
            while True:
                if self._stop_process_forever:
                    return
                self.reactor.process_once(timeout)
        self.reactor.process_forever = process_forever

        self._stop_process_forever = False
        self.channels_to_join = channels
        self.nickname = nickname
        self.nickpass = nickpass
        self.auth_type = auth_type
        self.server = server
        self.net_name = net_name
        self.port = port
        self.watchers = watchers
        self.last_mention = {}
        self.count_per_channel = {}
        self.spam_threshold = 15
        self.key_template = '{kind}{channel}{number}'
        self.ping_configured = False

    def shutdown(self):
        self._stop_process_forever = True
        self.reactor.disconnect_all()

    def _log_warning(self, msg):
        irc_client_logger.warning("(%s) %s" % (self.net_name, msg))

    def _log_info(self, msg):
        irc_client_logger.info("(%s) %s" % (self.net_name, msg))

    def _log_debug(self, msg):
        irc_client_logger.debug("(%s) %s" % (self.net_name, msg))

    def _log_error(self, msg):
        irc_client_logger.error("(%s) %s" % (self.net_name, msg))

    def on_privnotice(self, c, e):
        self._log_info("PRIVNOTICE: %s" % e.arguments[0])

    def on_nicknameinuse(self, c, e):
        # TODO: Try to retake nick? Or use a different one?
        # Probably best to try to retake nick, see gerrit bot
        # for implementation reference.
        pass

    def on_error(self, c, e):
        error = ""
        if len(e.arguments) > 0:
            error = e.arguments[0]
        else:
            error = str(e)
        self._log_error("ERROR: %s" % error)

    def on_welcome(self, connection, event):
        if not self.ping_configured:
            connection.set_keepalive(10)
            self.ping_configured = True

        if self.nickpass:
            if (not self.auth_type) or self.auth_type.lower() == 'nickserv':
                connection.privmsg('NickServ', 'IDENTIFY {password}'.format(
                    password=self.nickpass))

        self._join_channels(connection)

    def _join_channels(self, connection):
        for ch in self.channels_to_join:
            connection.join(ch)

    def on_nochanmodes(self, connection, event):
        # We couldn't join a channel, wait and retry
        timeout = 10
        self._log_info("NOCHANMODES retry to join in %s seconds" % timeout)
        time.sleep(timeout)
        self._join_channels(connection)

    def on_disconnect(self, connection, event):
        if not self._stop_process_forever:
            timeout = 10
            self._log_info("DISCONNECT reconnecting in %s seconds" % timeout)
            connected = False
            while not connected:
                # Wait a bit to avoid throttling
                time.sleep(timeout)
                try:
                    connection.reconnect()
                except irc.client.ServerConnectionError as e:
                    self._log_error(
                        "Failed to reconnect. Reconnecting in %s seconds."
                        "Reason: %s" % (timeout, e))
                else:
                    connected = True

    def _update_count(self, channel):
        count = self.count_per_channel.get(channel, 0) + 1
        self.count_per_channel[channel] = count

    def on_pubmsg(self, c, e):
        on_channel = e.target
        self._log_info("PUBMSG on channel %s: %s" % (
            on_channel, e.arguments[0]))

        if not self.watchers:
            return

        self._update_count(on_channel)

        for w in self.watchers:
            if not (w['network'] == self.net_name and
                    w['channel'] == on_channel):
                continue

            msg = e.arguments[0].split()
            mr_regex = r'!([0-9]+)'
            issue_regex = r'#([0-9]+)'
            for m in msg:
                issue_match = re.match(issue_regex, m)
                if issue_match:
                    self._log_info("PUBMSG contains ISSUE mention (%s)" % m)
                    self._fetch_and_say(c, 'issue', issue_match.group(1), w)

                mr_match = re.match(mr_regex, m)
                if mr_match:
                    self._log_info("PUBMSG contains MR mention (%s)" % m)
                    self._fetch_and_say(c, 'mr', mr_match.group(1), w)

            # Only one watcher allowed per channel. Stop.
            break

    def _mentioned_recently(self, channel, kind, number):
        key = self.key_template.format(
                kind=kind, channel=channel, number=number)
        last_time = self.last_mention.get(key)
        if last_time is None:
            return False
        if ((self.count_per_channel.get(channel, 0)-last_time) <=
                self.spam_threshold):
            return True
        return False

    def _update_mentions(self, channel, kind, number):
        key = self.key_template.format(
                kind=kind, channel=channel, number=number)
        self.last_mention[key] = self.count_per_channel.get(channel, 0)

    def _fetch_and_say(self, c, kind, number, watcher):
        server = watcher.get('server', 'https://gitlab.com')
        target = watcher['channel']
        project_encoded = urllib.parse.quote(watcher['project'], safe='')

        if self._mentioned_recently(target, kind, number):
            self._log_debug("_fetch_and_say decides not to react")
            return

        if kind == 'issue':
            url_template = 'api/v4/projects/{project}/issues/{number}'
            prefix_template = 'Issue #{number}:'
        elif kind == 'mr':
            url_template = 'api/v4/projects/{project}/merge_requests/{number}'
            prefix_template = 'MR !{number}:'

        url = urllib.parse.urljoin(server, url_template.format(
            project=project_encoded, number=number))

        self._log_debug("_fetch_and_say will query %s" % url)

        status, info = self._fetch_gitlab_info(url)
        if status != 200:
            self._log_error("Failed to query %s" % url)
            return

        self._log_info("Ttile %s" % info['title'])
        self._log_info("URL   %s" % info['web_url'])
        prefix = prefix_template.format(number=number)
        info_text = '{prefix} {title} {url}'.format(
                prefix=prefix, title=info['title'], url=info['web_url'])
        self._log_debug("_fetch_and_say sending to %s - %s" % (
            target, info_text))
        c.privmsg(target, info_text)
        self._update_mentions(target, kind, number)

    def _fetch_gitlab_info(self, url):
        data = requests.get(url)
        return data.status_code, data.json()


def connect_networks(networks, watchers):
    """ Connects to all the networks configured in the config file.

    Returns a dictionary using the same keys as in the config file
    containing process and bot object.
    """

    print("conf taken %s " % networks)
    result = {}
    for net in networks:
        server = networks[net]['url']
        port = networks[net]['port']
        nick = networks[net]['nick']
        channels = networks[net]['channels']
        password = networks[net].get('pass')
        auth_type = networks[net].get('auth')

        # TODO: Only use password if auth is set to 'sasl'
        bot = MyIRCClient(channels, nick, server, net, port=port,
                          watchers=watchers, nickpass=password,
                          auth_type=auth_type)
        irc_client_logger.info('Starting client for server %s' % server)
        thread = threading.Thread(target=bot.start)
        thread.start()

        result[net] = {
            'process': thread,
            'bot': bot
        }

    return result
