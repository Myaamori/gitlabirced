from behave import use_fixture
from behave_gitlabirced.fixtures import irc_server, gitlab_api


def before_all(context):
    context.server_a = use_fixture(irc_server, context, 8888)
    context.server_b = use_fixture(irc_server, context, 6666)
    context.api = use_fixture(gitlab_api, context, 9999)


def before_scenario(context, scenario):
    context.server_a.clean_messages()
    context.server_b.clean_messages()
