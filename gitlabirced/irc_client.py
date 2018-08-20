import irc.strings
import irc.client

from multiprocessing import Process
import sys


class MyIRCClient(irc.client.SimpleIRCClient):
    def __init__(self, channel, nickname, server, net_name, port=6667):
        irc.client.SimpleIRCClient.__init__(self)
        self.channel = channel
        self.nickname = nickname
        self.server = server
        self.net_name = net_name
        self.port = port

    def on_welcome(self, connection, event):
        connection.join(self.channel)

    def on_disconnect(self, connection, event):
        sys.exit(0)

    def on_pubmsg(self, c, e):
        print('on pubmsg')
        print('received via', self.net_name)
        print(c, e)


def connect_networks(networks):
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
        # TODO: get better the channels to connect for a given network
        channel = '##ironfoot'

        # TODO: Pass all the channels here, to connect later
        bot = MyIRCClient(channel, nick, server, net, port)
        bot.connect(server, port, nick)
        print("Starting %s" % server)
        thread = Process(target=bot.start)
        thread.start()

        result[net] = {
            'process': thread,
            'bot': bot
        }

    return result
