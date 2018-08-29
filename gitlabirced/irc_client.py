import irc.strings
import irc.client
import irc.bot

import logging
from threading import Thread
import re
import requests
import urllib

irc_client_logger = logging.getLogger(__name__)


class MyIRCClient(irc.bot.SingleServerIRCBot):
    def __init__(self, channels, nickname, server, net_name, port=6667,
                 watchers=None, nickpass=None):

        spec = irc.bot.ServerSpec(server, port, nickpass)
        irc.bot.SingleServerIRCBot.__init__(
            self, [spec], nickname, nickname)

        self.channels_to_join = channels
        self.nickname = nickname
        self.nickpass = nickpass
        self.server = server
        self.net_name = net_name
        self.port = port
        self.watchers = watchers
        self.last_mention = {}
        self.count_per_channel = {}
        self.spam_threshold = 15
        self.key_template = '{kind}{channel}{number}'
        self.ping_configured = False

    def _log_warning(self, msg):
        irc_client_logger.warning("(%s) %s" % (self.net_name, msg))

    def _log_info(self, msg):
        irc_client_logger.info("(%s) %s" % (self.net_name, msg))

    def _log_error(self, msg):
        irc_client_logger.error("(%s) %s" % (self.net_name, msg))

    def on_privnotice(self, c, e):
        self._log_info("PRIVNOTICE: %s" % e.arguments[0])

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
            # TODO: Only if auth is 'NickServ'
            connection.privmsg('NickServ', 'IDENTIFY {password}'.format(
                password=self.nickpass))

        for ch in self.channels_to_join:
            connection.join(ch)

    def on_disconnect(self, connection, event):
        connection.reconnect()

    def _update_count(self, channel):
        count = self.count_per_channel.get(channel, 0) + 1
        self.count_per_channel[channel] = count

    def on_pubmsg(self, c, e):
        print('on pubmsg')
        on_channel = e.target
        print('received via', self.net_name, 'channel', on_channel)

        if not self.watchers:
            return

        self._update_count(on_channel)

        for w in self.watchers:
            if not (w['network'] == self.net_name and
                    w['channel'] == on_channel):
                continue

            msg = e.arguments[0].split()
            mr_regex = r'#([0-9]+)'
            issue_regex = r'!([0-9]+)'
            for m in msg:
                issue_match = re.match(mr_regex, m)
                if issue_match:
                    print('MR')
                    print(m)
                    self._fetch_and_say(c, 'mr', issue_match.group(1), w)

                mr_match = re.match(issue_regex, m)
                if mr_match:
                    print('ISSUE')
                    print(m)
                    self._fetch_and_say(c, 'issue', mr_match.group(1), w)

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
            return

        if kind == 'issue':
            url_template = 'api/v4/projects/{project}/issues/{number}'
            prefix_template = 'Issue !{number}:'
        elif kind == 'mr':
            url_template = 'api/v4/projects/{project}/merge_requests/{number}'
            prefix_template = 'MR #{number}:'

        url = urllib.parse.urljoin(server, url_template.format(
            project=project_encoded, number=number))
        print(url)

        status, info = self._fetch_gitlab_info(url)
        if status != 200:
            return

        print('Title', info['title'])
        print('URL', info['web_url'])
        prefix = prefix_template.format(number=number)
        info_text = '{prefix} {title} {url}'.format(
                prefix=prefix, title=info['title'], url=info['web_url'])
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

        # TODO: Only use password if auth is set to 'sasl'
        bot = MyIRCClient(channels, nick, server, net, port=port,
                          watchers=watchers, nickpass=password)
        print("Starting %s" % server)
        thread = Thread(target=bot.start)
        thread.start()

        result[net] = {
            'process': thread,
            'bot': bot
        }

    return result
