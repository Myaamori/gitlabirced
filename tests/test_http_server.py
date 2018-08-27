import urllib.parse
import json

from helpers_http_server import BaseServerTestCase
from fake_helpers import FakeBot


class BaseHTTPServerTestCase(BaseServerTestCase):

    def setUp(self):
        self.token = 12345
        self.hooks = [
            {
                'project': 'palvarez89/definitions',
                'network': 'freenode',
                'branches': 'master',
                'reports': {
                    '#ironpush': ['push'],
                    '#ironissue': ['issue'],
                    '#ironmerge': ['merge_request']
                },
            }
        ]

        self.bots = {
            'freenode': {
                'bot': FakeBot()
            }
        }
        super(BaseHTTPServerTestCase, self).setUp()

    def test_get_disabled(self):
        res = self.request('/', method='GET')
        self.assertEqual(res.status, 501)

    def test_post_no_json(self):
        params = urllib.parse.urlencode(
            {'@number': 12524, '@type': 'issue', '@action': 'show'}
        )
        headers = {"X-Gitlab-Token": self.token}
        res = self.request('', method='POST', body=params, headers=headers)
        self.assertEqual(res.status, 400)
        self.assertEqual(res.reason, "JSON data couldn't be parsed")

    def test_post_no_token(self):
        headers = {"Content-type": "application/x-www-form-urlencoded",
                   "Accept": "text/plain"}
        res = self.request('', method='POST', headers=headers)
        self.assertEqual(res.status, 400)
        self.assertEqual(res.reason, "'X-Gitlab-Token' header not found")

    def test_post_wrong_token(self):
        headers = {"X-Gitlab-Token": "9999"}
        res = self.request('', method='POST', headers=headers)
        self.assertEqual(res.status, 401)
        self.assertEqual(res.reason, "Gitlab token not authorized")

    def test_post_no_object_kind(self):
        params = {'something_else': 'push'}
        headers = {"X-Gitlab-Token": self.token}
        params_json = json.dumps(params)
        res = self.request('', method='POST', body=params_json,
                           headers=headers)
        self.assertEqual(res.status, 400)
        self.assertEqual(res.reason, "Missing 'object_kind'")

    def test_post_unsupported_object_kind(self):
        params = {'object_kind': 'foo'}
        headers = {"X-Gitlab-Token": self.token}
        params_json = json.dumps(params)
        res = self.request('', method='POST', body=params_json,
                           headers=headers)
        self.assertEqual(res.status, 400)
        self.assertEqual(res.reason, "object_kind 'foo' not supported")

    def _post_json(self, filename):
        with open(filename, 'r') as json_file:
            json_push = json.load(json_file)
        headers = {"X-Gitlab-Token": self.token}
        params_json = json.dumps(json_push)
        self.request('', method='POST', body=params_json, headers=headers)

    def test_post_push(self):
        self._post_json('tests/data/push.json')
        exp = ["(#ironpush) jsmith pushed on Diaspora@master: 4 commits "
               "(last: fixed readme)"]
        self.assertEqual(
            self.bots['freenode']['bot'].connection.privmsgs['#ironpush'], exp)

    def test_post_issue(self):
        self._post_json('tests/data/issue.json')
        exp = ["(#ironissue) root opened issue #23 (New API: "
               "create/update/delete file) on Gitlab Test "
               "http://example.com/diaspora/issues/23"]
        self.assertEqual(
            self.bots['freenode']['bot'].connection.privmsgs['#ironissue'],
            exp)

    def test_post_merge_request(self):
        self._post_json('tests/data/merge_request.json')
        exp = ["(#ironmerge) root opened MR !1 (ms-viewport->master: "
               "MS-Viewport) on Awesome Project "
               "http://example.com/diaspora/merge_requests/1"]
        self.assertEqual(
            self.bots['freenode']['bot'].connection.privmsgs['#ironmerge'],
            exp)
