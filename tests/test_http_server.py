import http.client
import urllib.parse
import json

from helpers_http_server import BaseServerTestCase


class BaseHTTPServerTestCase(BaseServerTestCase):

    def setUp(self):
        BaseServerTestCase.setUp(self)
        self.con = http.client.HTTPConnection(self.HOST, self.PORT)
        self.con.connect()

    def test_get_disabled(self):
        self.con.request('GET', '/')
        res = self.con.getresponse()
        self.assertEqual(res.status, 501)

    def test_post_no_json(self):
        params = urllib.parse.urlencode(
            {'@number': 12524, '@type': 'issue', '@action': 'show'}
        )
        headers = {"X-Gitlab-Token": "12345"}
        self.con.request("POST", "", body=params, headers=headers)
        res = self.con.getresponse()
        self.assertEqual(res.status, 400)
        self.assertEqual(res.reason, "JSON data couldn't be parsed")

    def test_post_no_token(self):
        headers = {"Content-type": "application/x-www-form-urlencoded",
                   "Accept": "text/plain"}
        self.con.request("POST", "", headers=headers)
        res = self.con.getresponse()
        self.assertEqual(res.status, 400)
        self.assertEqual(res.reason, "'X-Gitlab-Token' header not found")

    def test_post_wrong_token(self):
        headers = {"X-Gitlab-Token": "9999"}
        self.con.request("POST", "", headers=headers)
        res = self.con.getresponse()
        self.assertEqual(res.status, 401)
        self.assertEqual(res.reason, "Gitlab token not authorized")

    def test_post_no_object_kind(self):
        params = {'something_else': 'push'}
        headers = {"X-Gitlab-Token": "12345"}
        params_json = json.dumps(params)
        self.con.request("POST", "", body=params_json, headers=headers)
        res = self.con.getresponse()
        self.assertEqual(res.status, 400)
        self.assertEqual(res.reason, "Missing 'object_kind'")

    def test_post_unsupported_object_kind(self):
        params = {'object_kind': 'foo'}
        headers = {"X-Gitlab-Token": "12345"}
        params_json = json.dumps(params)
        self.con.request("POST", "", body=params_json, headers=headers)
        res = self.con.getresponse()
        self.assertEqual(res.status, 400)
        self.assertEqual(res.reason, "object_kind 'foo' not supported")
