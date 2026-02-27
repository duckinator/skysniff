import logging
import urllib.request

from . import version

def request(method, url, data, headers):
    if headers is None:
        headers = {}

    if isinstance(data, (dict, list)):
        data = json.dumps(data).encode()

    headers['User-Agent'] = f"skysniff/{version.__version__} (+https://github.com/duckinator/skysniff)"

    req = urllib.request.Request(url, data=data,
                                 headers=headers, method=method)

    with urllib.request.urlopen(req) as res:
        response = res.read().decode()

    return response

def get(url, headers={}):
    return request('GET', url, None, headers)

def post(url, data, headers={}):
    return request('POST', url, data, headers)
