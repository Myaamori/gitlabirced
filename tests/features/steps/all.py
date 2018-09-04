from behave import given, when, then, use_fixture
import irc.client
import logging
import random
import string
import time
import urllib

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

    def send_message(self, times=1):
        for i in range(times):
            self.connection.privmsg(self.target, self.message)
        # Give some time before dropping
        time.sleep(0.1)
        self.connection.quit("Using irc.client.py")


@given('a gitlabirced watcher')
def step_load_watcher(context):
    watcher = {}
    for row in context.table:
        watcher[row['key']] = row['value']
    watchers = context.conf.get('watchers', [])
    watchers.append(watcher)
    context.conf['watchers'] = watchers


@given('gitlabirced running')
def step_run_bot(context):
    watchers = context.conf.get('watchers', [])
    for watcher in watchers:
        watcher['server'] = "http://127.0.0.1:%s" % context.api.port
    context.bot = use_fixture(run_bot, context, context.conf)


@when('client comments "{message}" on "{network}" channel "{channel}"')
def step_client_comments(context, message, network, channel, times=1):
    irc_server = getattr(context, "irc_" + network)
    # Use a random nick every time, otherwise we will have
    # problems with race conditions, given that the client
    # won't disconnect before the new connection.
    nick = ''.join(random.choices(
        string.ascii_uppercase + string.digits, k=5))
    nick = "peter_%s" % nick
    c = IRCMessageSender(channel, message)
    c.connect(irc_server.host, irc_server.port, nick)
    c.send_message(times)


@when('client comments "{message}" on "{network}" channel "{channel}" '
      '"{times}" times')
def step_client_comments_multiple(context, message, network, channel, times):
    step_client_comments(context, message, network, channel, int(times))


@then('network "{network}" channel "{channel}" contains "{number}" messages')
def step_check_channel_number_messages(context, network, channel, number):
    irc_server = getattr(context, "irc_" + network)
    n = int(number)
    tries = 100
    timeout = 0.05
    for i in range(tries):
        actual = len(irc_server.messages.get(channel, []))
        if n != actual:
            time.sleep(timeout)
        else:
            break

    # Read again, just in case
    final = len(irc_server.messages.get(channel, []))
    logger.info(irc_server.messages.get(channel, []))
    assert n == final


@then('network "{network}" log contains "{number}" messages')
def step_check_log_number_messages(context, network, number):
    irc_server = getattr(context, "irc_" + network)
    n = int(number)
    tries = 100
    timeout = 0.05
    for i in range(tries):
        actual = len(irc_server.log)
        if n != actual:
            time.sleep(timeout)
        else:
            break

    # Read again, just in case
    final = len(irc_server.log)
    logger.info(irc_server.log)
    assert n == final


@then('network "{network}" channel "{channel}" last message is "{message}"')
def step_check_last_message(context, network, channel, message):
    irc_server = getattr(context, "irc_" + network)
    last = irc_server.messages[channel][-1]
    message = ":%s" % message
    logger.info(message)
    logger.info(last)
    assert last == message


@then('network "{network}" last long log message is')
def step_check_last_long_log_message(context, network):
    irc_server = getattr(context, "irc_" + network)
    last = irc_server.log[-1]
    message = context.text
    logger.info(message)
    logger.info(last)
    assert last == message


@then('network "{network}" channel "{channel}" last message is about '
      'issue "{issuenumber}" project "{project}"')
def step_check_last_message_issue(context, network, channel, issuenumber,
                                  project):
    project_safe = urllib.parse.quote(project, safe='')
    project_title = project_safe.title()

    expected = ('Issue #{n}: Api V4 Projects {project_title} Issues '
                '{n} http://fakegitlab.com/api/v4/projects/{project_safe}'
                '/issues/{n}')
    expected = expected.format(n=issuenumber,
                               project_title=project_title,
                               project_safe=project_safe)
    step_check_last_message(context, network, channel, expected)


@then('network "{network}" channel "{channel}" last message is '
      'about merge request "{mrnumber}" project "{project}"')
def step_check_last_message_mr(context, network, channel, mrnumber, project):

    project_safe = urllib.parse.quote(project, safe='')
    project_title = project_safe.title()

    expected = ('MR !{n}: Api V4 Projects {project_title} Merge_Requests '
                '{n} http://fakegitlab.com/api/v4/projects/{project_safe}'
                '/merge_requests/{n}')
    expected = expected.format(n=mrnumber,
                               project_title=project_title,
                               project_safe=project_safe)
    step_check_last_message(context, network, channel, expected)
