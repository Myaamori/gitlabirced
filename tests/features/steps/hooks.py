from behave import given, when, then
import json
import logging
import requests

logger = logging.getLogger(__name__)


@given('a gitlabirced hook')
def step_load_hook(context):
    reports = {}
    hook = {}
    for row in context.table:
        key = row['key']
        value = row['value']
        if key == 'report':
            channel, hooks = value.split(':')
            reports[channel] = hooks
            continue
        hook[key] = value
    hook['reports'] = reports

    all_hooks = context.conf.get('hooks', [])
    all_hooks.append(hook)
    context.conf['hooks'] = all_hooks


@when('a push hook about project "{project}" branch "{branch}" is received')
def step_send_push_hook(context, project, branch):
    with open('data/push.json') as json_file:
        data = json.load(json_file)
    data['project']['path_with_namespace'] = project
    data['project']['name'] = project.replace('/', ' ').title()
    data['ref'] = 'refs/heads/%s' % branch

    _send_request(data)


@when('an issue hook about project "{project}" is received')
def step_send_issue_hook(context, project):
    with open('data/issue.json') as json_file:
        data = json.load(json_file)
    data['project']['path_with_namespace'] = project
    data['project']['name'] = project.replace('/', ' ').title()

    _send_request(data)


@when('a merge request hook about project "{project}" is received')
def step_send_merge_request_hook(context, project):
    with open('data/merge_request.json') as json_file:
        data = json.load(json_file)
    data['object_attributes']['target']['path_with_namespace'] = project
    data['object_attributes']['target']['name'] = (
        project.replace('/', ' ').title())

    _send_request(data)


@then('network "{network}" channel "{channel}" last long message is')
def step_check_last_long_message(context, network, channel):
    irc_server = getattr(context, "irc_" + network)
    last = irc_server.messages[channel][-1]
    message = ":%s" % context.text
    logger.info(message)
    logger.info(last)
    assert last == message


def _send_request(data):
    headers = {'X-Gitlab-Token': '12345'}
    requests.post('http://127.0.0.1:1337', json=data, headers=headers)
