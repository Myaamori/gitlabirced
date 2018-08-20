import unittest
import http.client

from helpers_http_server import BaseServerTestCase
from gitlabirced.http_server import MyHTTPServer, RequestHandler


class BaseHTTPServerTestCase(BaseServerTestCase):

    def setUp(self):
        BaseServerTestCase.setUp(self)
        self.con = http.client.HTTPConnection(self.HOST, self.PORT)
        self.con.connect()

    def test_command(self):
        self.con.request('GET', '/')
        res = self.con.getresponse()
        self.assertEqual(res.status, 501)

