import irc.strings
import irc.client

from multiprocessing import Process
import re
import requests
import urllib
import sys


class MyIRCClient(irc.client.SimpleIRCClient):
    def __init__(self, channels, nickname, server, net_name, port=6667,
                 watchers=None):
        irc.client.SimpleIRCClient.__init__(self)
        self.channels = channels
        self.nickname = nickname
        self.server = server
        self.net_name = net_name
        self.port = port
        self.watchers = watchers
        self.last_mention = {}
        self.count_per_channel = {}
        self.spam_threshold = 15
        self.key_template = '{kind}{channel}{number}'

    def on_welcome(self, connection, event):
        for ch in self.channels:
            connection.join(ch)

    def on_disconnect(self, connection, event):
        sys.exit(0)

    def _update_count(self, channel):
        count = self.count_per_channel.get(channel, 0) + 1
        self.count_per_channel[channel] = count

    def on_pubmsg(self, c, e):
        print('on pubmsg')
        on_channel = e.target
        print('received via', self.net_name, 'channel', on_channel)

        if not self.watchers:
            return

        for w in self.watchers:
            if not (w['network'] == self.net_name and
                    w['channel'] == on_channel):
                continue

            self._update_count(on_channel)

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
        if not last_time:
            return False
        if (self.count_per_channel[channel]-last_time) <= self.spam_threshold:
            return True
        return False

    def _update_mentions(self, channel, kind, number):
        key = self.key_template.format(
                kind=kind, channel=channel, number=number)
        self.last_mention[key] = self.count_per_channel[channel]

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

        data = requests.get(url)
        info = data.json()
        status = data.status_code
        if status != 200:
            return

        print('Title', info['title'])
        print('URL', info['web_url'])
        prefix = prefix_template.format(number=number)
        info_text = '{prefix} {title} {url}'.format(
                prefix=prefix, title=info['title'], url=info['web_url'])
        c.privmsg(target, info_text)
        self._update_mentions(target, kind, number)


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

        bot = MyIRCClient(channels, nick, server, net, port, watchers)
        bot.connect(server, port, nick)
        print("Starting %s" % server)
        thread = Process(target=bot.start)
        thread.start()

        result[net] = {
            'process': thread,
            'bot': bot
        }

    return result
