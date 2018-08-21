from http.server import HTTPServer
from http.server import BaseHTTPRequestHandler
import json
import logging


class MyHTTPServer(HTTPServer):

    def __init__(self, token, hooks, bots, *args, **kw):
        HTTPServer.__init__(self, *args, **kw)
        self.token = token
        self.hooks = hooks
        self.bots = bots


class RequestException(Exception):
    def __init__(self, code, status):
        self.code = code
        self.status = status
        logging.error('%s - %s' % (self.code, self.status))


class RequestHandler(BaseHTTPRequestHandler):
    """A POST request handler."""

    def _check_token(self):
        # get gitlab secret token
        gitlab_token_header = self.headers.get('X-Gitlab-Token')

        if not gitlab_token_header:
            raise RequestException(400, "'X-Gitlab-Token' header not found")

        # get token from config file
        gitlab_token = str(self.server.token)

        # Check if the gitlab token is valid
        if gitlab_token_header != gitlab_token:
            raise RequestException(401, "Gitlab token not authorized")

    def _check_and_get_request_data(self):
        # get payload
        header_length = int(self.headers.get('content-length', "0"))
        json_payload = self.rfile.read(header_length)

        if len(json_payload) == 0:
            raise RequestException(400, "Request didn't contain data")

        try:
            json_params = json.loads(json_payload)
        except json.decoder.JSONDecodeError:
            raise RequestException(400, "JSON data couldn't be parsed")

        object_kind = json_params.get('object_kind')
        if not object_kind:
            raise RequestException(400, "Missing 'object_kind'")

        if object_kind not in ['push', 'issue', 'merge_request']:
            raise RequestException(400, "object_kind '%s' not supported" %
                                   object_kind)
        return json_params

    def do_POST(self):
        hooks = self.server.hooks
        print(hooks)
        logging.info("Hook received")

        try:
            self._check_token()
            json_params = self._check_and_get_request_data()
            handler = getattr(
                self, '_handle_%s' % json_params.get('object_kind'))
            handler(json_params)
        except RequestException as re:
            self.send_response(re.code, re.status)
        except Exception:
            self.send_response(500, "Internal server error")
        finally:
            self.end_headers()

    def _handle_push(self, json_params):
        print('handling push')
        hooks = self.server.hooks
        bots = self.server.bots

        try:
            project = json_params['project']['path_with_namespace']
            project_name = json_params['project']['name']
            user = json_params['user_username']
            commits = json_params['commits']
            num_commits = json_params.get('total_commits_count')
            branch_name = json_params['ref']
            ref_after = json_params['after']
            ref_prefix = 'refs/heads/'
            if branch_name.startswith(ref_prefix):
                branch_name = branch_name[len(ref_prefix):]
        except KeyError:
            raise RequestException(400, "Missing data in the request")

        if not num_commits:
            # Branch created or deleted
            action = 'created'
            if ref_after == '0000000000000000000000000000000000000000':
                action = 'deleted'
            msg = ('{user} {action} branch {branch_name} on {project_name}.'
                   .format(user=user, action=action,
                           branch_name=branch_name,
                           project_name=project_name))
        else:
            last_commit = commits[-1]
            last_commit_msg = last_commit['message'].split('\n')[0]
            pre_msg = ('{user} pushed on {project_name}@{branch_name}:'
                       .format(user=user, project_name=project_name,
                               branch_name=branch_name))
            if num_commits == 1:
                msg = ('{pre_msg} {last_commit_msg}'
                       .format(pre_msg=pre_msg,
                               last_commit_msg=last_commit_msg))
            else:
                msg = ('{pre_msg} {num_commits} commits (last: '
                       '{last_commit_msg})'
                       .format(pre_msg=pre_msg,
                               num_commits=num_commits,
                               last_commit_msg=last_commit_msg))

        for h in hooks:
            if h['project'] == project:
                print('project found!!')
                network = h['network']
                reports = h['reports']
                branches = h['branches'].split()
                bot = bots[network]['bot']
                if branch_name not in branches:
                    continue
                for r in reports:
                    if 'push' in reports[r]:
                        print('sending to %s, in network %s' % (r, network))
                        bot.connection.privmsg(r, msg)

            else:
                print("not found", project)
        self.send_response(200, "OK")
