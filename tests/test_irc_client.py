import unittest

from gitlabirced.irc_client import MyIRCClient


class FakeConnection():
    def __init__(self):
        self.privmsgs = {}

    def privmsg(self, target, msg):
        msgs = self.privmsgs.get(target, [])
        msgs.append("(%s) %s" % (target, msg))
        self.privmsgs[target] = msgs


class BaseIRCClientTestCase(unittest.TestCase):
    def _fake_info(self, url):
        return self.code, {'title': self.title,
                           'web_url': url}

    def setUp(self):
        self.connection = FakeConnection()
        self.mycli = MyIRCClient([], 'nick', 'freenode.org', 'freenode')
        self.mycli._fetch_gitlab_info = self._fake_info

    def test_fetch_and_say(self):
        self.title = "Title of the mr"
        self.code = 200
        target = '#target'

        watcher = {'channel': target, 'project': 'namespace/project'}
        self.mycli._fetch_and_say(self.connection, 'mr', '12', watcher)

        self.assertEqual(len(self.connection.privmsgs[target]), 1)
        self.assertEqual(
            self.connection.privmsgs[target][-1],
            "(#target) MR #12: Title of the mr https://gitlab.com/api"
            "/v4/projects/namespace%2Fproject/merge_requests/12")

        self.mycli._fetch_and_say(self.connection, 'mr', '12', watcher)
        self.assertEqual(len(self.connection.privmsgs[target]), 1)
