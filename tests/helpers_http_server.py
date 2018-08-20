import unittest
import pytest

from test import support
threading = support.import_module('threading')

import http.client
import os
import sys

from gitlabirced.http_server import MyHTTPServer, RequestHandler


class BaseServerTestCase(unittest.TestCase):
    def setUp(self):
        self._threads = support.threading_setup()
        os.environ = support.EnvironmentVarGuard()
        self.server_started = threading.Event()
        self.thread = TestServerThread(self)
        self.thread.start()

        sys.stderr.write('waiting thread\n')
        self.server_started.wait()
        sys.stderr.write('waiting thread finished\n')

    def tearDown(self):
        self.thread.stop()
        self.thread = None
        os.environ.__exit__()
        support.threading_cleanup(*self._threads)

    def request(self, uri, method='GET', body=None, headers={}):
        self.connection = http.client.HTTPConnection(self.HOST, self.PORT)
        self.connection.request(method, uri, body, headers)
        return self.connection.getresponse()


class TestServerThread(threading.Thread):
    def __init__(self, test_object):
        threading.Thread.__init__(self)
        self.test_object = test_object

    def run(self):
        token = 12345
        hooks = {}
        all_bots = {}
        sys.stderr.write('starting thread\n')
        self.server = MyHTTPServer(token, hooks, all_bots,
                                   ('localhost', 0),
                                   RequestHandler)

        self.test_object.HOST, self.test_object.PORT = self.server.socket.getsockname()
        sys.stderr.write('thread started\n')
        sys.stderr.write('HOST %s\n' % self.test_object.HOST)
        sys.stderr.write('PORT %s\n' % self.test_object.PORT)
        self.test_object.server_started.set()
        self.test_object = None
        try:
            self.server.serve_forever(0.05)
        finally:
            self.server.server_close()

    def stop(self):
        self.server.shutdown()