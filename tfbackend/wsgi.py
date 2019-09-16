import datetime
import json
import traceback
from urllib.parse import parse_qs

from . import fs

class OuptutEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime.datetime):
            return o.isoformat()
        return json.JSONEncoder.default(self, o)


class UnsupportedRequestError(RuntimeError):
    pass


class Application(object):
    def __init__(self, executor):
        self.executor = executor

    def __call__(self, env, start_response):
        # env[]: 'REQUEST_METHOD', 'wsgi.input'?, 'REQUEST_URI', 'HTTP_ACCEPT', 'wsgi.errors'?, 'HTTP_ACCEPT_LANGUAGE', 'wsgi.file_wrapper'?, 'PATH_INFO'?

        #some useful info (TODO: standard logging?)
        print('REQUEST_METHOD: ' + str(env['REQUEST_METHOD']))
        print('REQUEST_URI: ' + str(env['REQUEST_URI']))
        print('HTTP_ACCEPT: ' + str(env['HTTP_ACCEPT']))
        print('QUERY_STRING: ' + str(env.get('QUERY_STRING')))
        request_method = env['REQUEST_METHOD']
        request_uri = env['REQUEST_URI']
        if request_uri and request_uri[0]=='/':
            request_uri = request_uri[1:]
        request_uri_items = request_uri.split('/')
        request_params = parse_qs(env.get('QUERY_STRING', '')) # dict(p.split('=') for p in env.get('QUERY_STRING', '').split('&') if p)

        result = None

        # prase the url into verb and filename
        request_verb = ''
        request_filename = None
        if request_uri_items:
            request_verb = request_uri_items[0].lower()
            request_filename = '/'.join(request_uri_items[1:])

        # start to read the body
        body_content = None
        if request_method in ['POST', 'LOCK']:
            body_content = env['wsgi.input'].read()
        
        # extract the various bits interesting below, in particular the request id (lock id) that may come from URL params or the body
        file_content = body_content
        request_id = request_params.get('ID')
        request_content = body_content
        if body_content and not request_id:
            body_data = json.loads(body_content)
            request_id = body_data.get('ID')
        elif request_id:
            request_id = request_id[0]

        # dispatch depending on verb and method
        try:
            if request_verb=='get':
                if request_method=='GET':
                    result = self.executor.read(request_filename)
                elif request_method=='POST':
                    self.executor.write(request_filename, file_content, request_id)
                    result = "OK"
                elif request_method=='LOCK':
                    self.executor.lock(request_filename, request_content)
                    result = "OK"
                elif request_method=='UNLOCK':
                    self.executor.unlock(request_filename, request_id)
                    result = "OK"
                else:
                    raise UnsupportedRequestError('Unsupported REQUEST_METHOD: ' + str(request_method))
            elif request_verb=='lock':
                self.executor.lock(request_filename, request_content)
                result = "OK"
            elif request_verb=='unlock':
                self.executor.unlock(request_filename, request_id)
                result = "OK"
            else:
                raise UnsupportedRequestError('Unsupported verb: ' + str(request_verb))
        except fs.FilePermissionError as e:
            start_response('400 Not Permitted', [('Content-Type','application/json')])
            result = str(e)
        except fs.FileLockedError as e:
            start_response('423 Locked', [('Content-Type','application/json')])
            result = str(e)
        except fs.LockConflictError as e:
            start_response('409 Lock Conflict', [('Content-Type','application/json')])
            result = str(e)
        except UnsupportedRequestError as e:
            start_response('400 Unexpected', [('Content-Type','application/json')])
        except Exception as e:
            print('Unexpected exception caught: ' + traceback.format_exc(e))
            start_response('500 Internal Error', [('Content-Type','application/json')])
            result = 'Internal Error'
        else:
            start_response('200 OK', [('Content-Type','application/json')])

        # final output
        return [json.dumps(result, cls=OuptutEncoder)]

app = Application(fs.Fs())
