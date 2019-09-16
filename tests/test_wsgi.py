import io
import json
import unittest

from tfbackend import fs
from tfbackend import wsgi

TEST_FILE = '/x/y/z/state.tf'
FILE_CONTENT = '''{}'''
DEFAULT_HEADERS = {
    'Content-Type': 'application/json',
}
LOCK_ID = '115affe6-18e3-f6b1-b4d2-e23b04f12604'
LOCK_CONTENT = '''{"ID":"115affe6-18e3-f6b1-b4d2-e23b04f12604","Operation":"OperationTypeApply","Info":"","Who":"admin","Version":"0.11.13","Created":"2019-09-16T14:32:16.7858102Z","Path":""}'''


class TestApplication(unittest.TestCase):
    def test_read(self):
        app = wsgi.Application(fs.Fs())

        env = self.get('/get' + TEST_FILE)
        response = app(env, self.check_answer('200', DEFAULT_HEADERS))
        self.assertEqual(response, ['null'])

    def test_write(self):
        app = wsgi.Application(fs.Fs())

        env = self.post('/get' + TEST_FILE, FILE_CONTENT)
        response = app(env, self.check_answer('400', DEFAULT_HEADERS))
        self.assertTrue('lock' in response[0].lower())
        self.assertTrue('required' in response[0].lower())

        env = self.lock('/get' + TEST_FILE, LOCK_CONTENT)
        response = app(env, self.check_answer('200', DEFAULT_HEADERS))

        env = self.post('/get' + TEST_FILE, FILE_CONTENT, {'ID': LOCK_ID})
        response = app(env, self.check_answer('200', DEFAULT_HEADERS))

        env = self.unlock('/get' + TEST_FILE, '', {'ID': LOCK_ID})
        response = app(env, self.check_answer('200', DEFAULT_HEADERS))

    def check_answer(self, expected_message, expected_headers):
        def check(message, headers):
            self.assertTrue(message.startswith(expected_message), 'Expecting message to start with ' + str(expected_message))
            headers = dict(headers)
            for k, v in expected_headers.items():
                self.assertEqual(headers[k], v, 'Expected header "' + str(k) + '" to be "' + str(v) + '"')
        return check

    def query(self, method, url, content=None, params={}):
        env = {
            'REQUEST_METHOD': method,
            'REQUEST_URI': url,
            'HTTP_ACCEPT': 'application/json',
            'QUERY_STRING': '&'.join('='.join([k, v]) for k, v in params.items()),
        }
        if content:
            env['wsgi.input'] = io.StringIO(content)
        return env
    def get(self, url, params={}):
        return self.query('GET', url, params=params)
    def post(self, url, content, params={}):
        return self.query('POST', url, content=content, params=params)
    def lock(self, url, content, params={}):
        return self.query('LOCK', url, content=content, params=params)
    def unlock(self, url, content, params={}):
        return self.query('UNLOCK', url, content=content, params=params)
