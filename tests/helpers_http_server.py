import http.client
import sys
import threading
import unittest

from gitlabirced.http_server import MyHTTPServer, RequestHandler


class BaseServerTestCase(unittest.TestCase):
    def setUp(self):
        self.server_started = threading.Event()
        self.thread = TestServerThread(self)
        self.thread.start()

        sys.stderr.write('waiting thread\n')
        self.server_started.wait()
        sys.stderr.write('waiting thread finished\n')

    def tearDown(self):
        self.thread.stop()
        self.thread = None

    def request(self, uri, method='GET', body=None, headers={}):
        self.connection = http.client.HTTPConnection(self.HOST, self.PORT)
        self.connection.request(method, uri, body, headers)
        return self.connection.getresponse()


class TestServerThread(threading.Thread):
    def __init__(self, test_object):
        threading.Thread.__init__(self)
        self.test_object = test_object

    def run(self):
        sys.stderr.write('starting thread\n')
        self.server = MyHTTPServer(self.test_object.token,
                                   self.test_object.hooks,
                                   self.test_object.bots,
                                   ('localhost', 0),
                                   RequestHandler)

        self.test_object.HOST, self.test_object.PORT = (
            self.server.socket.getsockname())
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
