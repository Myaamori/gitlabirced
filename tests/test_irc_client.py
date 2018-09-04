import unittest
from irc.client import Event

from fake_helpers import FakeConnection
from gitlabirced.irc_client import MyIRCClient


class BaseIRCClientTestCase(unittest.TestCase):
    def _fake_info(self, url):
        return self.code, {'title': self.title,
                           'web_url': url}

    def setUp(self):
        self.connection = FakeConnection()
        self.target = '#target'

        watcher = {'network': 'freenode',
                   'channel': self.target,
                   'project': 'namespace/project'}
        self.mycli = MyIRCClient(
            [self.target], 'nick', 'freenode.org', 'freenode',
            watchers=[watcher], nickpass="p4ssw0rd")

        self.mycli._fetch_gitlab_info = self._fake_info

    def test_on_pubmsg_irrelevant(self):
        event = Event('pubmsg', '@somebody', self.target, ['a message'])

        # Receive a pubmsg
        self.mycli.on_pubmsg(self.connection, event)
        self.assertEqual(self.mycli.count_per_channel[self.target], 1)

        # Receive a second pubmsg
        self.mycli.on_pubmsg(self.connection, event)
        self.assertEqual(self.mycli.count_per_channel[self.target], 2)

        self.assertEqual(self.connection.privmsgs, {})

    def test_on_pubmsg_issue(self):
        self.title = "Title of the issue"
        self.code = 200

        expected_msg = ("(#target) Issue #12: Title of the issue https://"
                        "gitlab.com/api/v4/projects/namespace%2Fproject/"
                        "issues/12")

        self._test_on_pubmsg_generic('show me #12 plz', expected_msg)

    def test_on_pubmsg_mr(self):
        self.title = "Title of the mr"
        self.code = 200

        expected_msg = ("(#target) MR !12: Title of the mr https://"
                        "gitlab.com/api/v4/projects/namespace%2Fproject/"
                        "merge_requests/12")

        self._test_on_pubmsg_generic('show me !12 plz', expected_msg)

    def _test_on_pubmsg_generic(self, msg, expected):
        event = Event('pubmsg', '@somebody', self.target, [msg])

        # Receive a message with an issue number tag
        self.mycli.on_pubmsg(self.connection, event)
        # Expect an answer from the bot
        self.assertEqual(self.mycli.count_per_channel[self.target], 1)
        self.assertEqual(len(self.connection.privmsgs[self.target]), 1)
        self.assertEqual(
            self.connection.privmsgs[self.target][-1], expected)

        # Receive 'spam_threshold' more messages
        for i in range(self.mycli.spam_threshold):
            self.mycli.on_pubmsg(self.connection, event)
            self.assertEqual(self.mycli.count_per_channel[self.target], 2 + i)
        # Expect the bot to stay quiet
        self.assertEqual(len(self.connection.privmsgs[self.target]), 1)

        # Receive the same message once more
        self.mycli.on_pubmsg(self.connection, event)
        # Expect the bot to reply again
        self.assertEqual(self.mycli.count_per_channel[self.target], 17)
        self.assertEqual(len(self.connection.privmsgs[self.target]), 2)
        self.assertEqual(
            self.connection.privmsgs[self.target][-1], expected)

    def test_on_welcome(self):
        event = Event('welcome', 'freenode.net', 'me', ['WELCOME!'])

        # Expect an IDENTIFY message to NickServ
        self.mycli.on_welcome(self.connection, event)
        self.assertEqual(
            self.connection.privmsgs['NickServ'][-1],
            "(NickServ) IDENTIFY p4ssw0rd")
        # Expect some channels joined
        self.assertEqual(
            self.connection.channels,
            [self.target])
