from behave import use_fixture
from behave_gitlabirced.fixtures import irc_server, gitlab_api

from gitlabirced.cli import load_config


def before_all(context):
    context.irc_freenode = use_fixture(irc_server, context)
    context.irc_gimpnet = use_fixture(irc_server, context)
    context.api = use_fixture(gitlab_api, context)
    context.conf = load_config('data/base.yaml')
    context.conf['networks']['freenode']['port'] = context.irc_freenode.port
    context.conf['networks']['gimpnet']['port'] = context.irc_gimpnet.port


def before_scenario(context, scenario):
    context.irc_freenode.clean_messages()
    context.irc_gimpnet.clean_messages()
    context.conf.pop('watchers', None)
    context.conf.pop('hooks', None)
