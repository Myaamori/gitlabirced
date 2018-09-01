from behave import given, when, then, use_fixture
import irc.client
import logging
import time

from behave_gitlabirced.fixtures import run_bot

logger = logging.getLogger(__name__)


class IRCMessageSender(irc.client.SimpleIRCClient):
    def __init__(self, target, message):
        self.target = target
        self.message = message
        super(IRCMessageSender, self).__init__()

    def connect(self, server, port, nickname):
        super(IRCMessageSender, self).connect(server, port, nickname)
        # Auto join target channel, otherwise we can't send messages
        self.connection.join(self.target)

    def send_message(self, target, message):
        self.connection.privmsg(self.target, self.message)
        self.connection.quit("Using irc.client.py")


@given('gitlabirced running using "{conf}"')
def step_run_bot(context, conf):
    context.bot = use_fixture(run_bot, context, conf)


@when('client comments "{message}" on channel "{channel}"')
def step_client_comments(context, message, channel):

    c = IRCMessageSender(channel, message)
    c.connect(context.server_a.host, context.server_a.port, 'peter')
    c.send_message('#ironfoot3', "!12")


@then('channel "{channel}" contains "{number}" messages')
def step_check_channel_number_messages(context, channel, number):
    n = int(number)
    tries = 20
    timeout = 0.05
    for i in range(tries):
        actual = len(context.server_a.messages[channel])
        if n != actual:
            time.sleep(timeout)
        else:
            break

    # Read again, just in case
    final = len(context.server_a.messages[channel])
    assert n == final


@then('channel "{channel}" last message is about issue "{issuenumber}"')
def step_check_last_message_issue(context, channel, issuenumber):
    last = context.server_a.messages[channel][-1]
    expected = (':Issue !12: Api V4 Projects Baserock%252Fdefinitions Issues '
                '12 http://fakegitlab.com/api/v4/projects/baserock%252F'
                'definitions/issues/12')
    assert last == expected
