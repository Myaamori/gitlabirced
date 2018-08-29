class FakeConnection():
    def __init__(self):
        self.privmsgs = {}
        self.channels = []

    def privmsg(self, target, msg):
        msgs = self.privmsgs.get(target, [])
        msgs.append("(%s) %s" % (target, msg))
        self.privmsgs[target] = msgs

    def join(self, channel):
        self.channels.append(channel)

    def set_keepalive(self, interval):
        pass


class FakeBot():
    def __init__(self):
        self.connection = FakeConnection()
