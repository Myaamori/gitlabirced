import irc.strings
import irc.client

from multiprocessing import Process
import re
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

    def on_welcome(self, connection, event):
        for ch in self.channels:
            connection.join(ch)

    def on_disconnect(self, connection, event):
        sys.exit(0)

    def on_pubmsg(self, c, e):
        print('on pubmsg')
        on_channel = e.target
        print('received via', self.net_name, 'channel', on_channel)

        if not self.watchers:
            return

        for w in self.watchers:
            if not (w['network'] == self.net_name and
                    w['channel'] == on_channel):
                # TODO count as line written, for repeated msgs safety
                continue

            msg = e.arguments[0].split()
            mr_regex = r'#[0-9]+'
            issue_regex = r'![0-9]+'
            for m in msg:
                if re.match(mr_regex, m):
                    print('MR')
                    print(m)

                elif re.match(issue_regex, m):
                    print('ISSUE')
                    print(m)

            # Only one watcher allowed per channel. Stop.
            break


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
