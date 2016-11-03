import json
import socket

from tornado import gen
from tornado.httpclient import HTTPClient, HTTPError
from tornado.netutil import Resolver

class UnixResolver(Resolver):
    """UnixResolver from https://gist.github.com/bdarnell/8641880"""
    def initialize(self, resolver, socket_path):
        self.resolver = resolver
        self.socket_path = socket_path

    def close(self):
        self.resolver.close()

    @gen.coroutine
    def resolve(self, host, port, *args, **kwargs):
        if host == 'unix+restuser':
            raise gen.Return([(socket.AF_UNIX, self.socket_path)])
        result = yield self.resolver.resolve(host, port, *args, **kwargs)
        raise gen.Return(result)

resolver = UnixResolver(resolver=Resolver(), socket_path='/var/run/restuser.sock')
client = HTTPClient(resolver=resolver)

def query_user(name):
    try:
       resp = client.fetch('http://unix+restuser/' + name, method='POST', body='{}')
    except HTTPError as e:
        print(e.response.code, e.response.body.decode('utf8', 'replace'))
        return
    user = json.loads(resp.body.decode('utf8', 'replace'))
    return user