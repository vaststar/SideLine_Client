from urllib import request
import json
class HTTPRequest(object):
    @staticmethod
    def get(url):

        header = {'Content-Type': 'application/json;charset=utf-8'}
        req = request.Request(url=url, headers=header, method="GET")
        res = request.urlopen(req).read()
        return json.loads(res.decode(encoding='utf-8'))

    @staticmethod
    def post(url,data):
        header = {'Content-Type': 'application/json;charset=utf-8'}
        req = request.Request(url=url, data=json.dumps(data).encode('utf-8'), headers=header,method="POST")
        res = request.urlopen(req).read()
        return json.loads(res.decode(encoding='utf-8'))

    @staticmethod
    def delete(url):
        header = {'Content-Type': 'application/json;charset=utf-8'}
        req = request.Request(url=url, dheaders=header,method="DELETE")
        res = request.urlopen(req).read()
        return json.loads(res.decode(encoding='utf-8'))

    @staticmethod
    def put(url,data):
        header = {'Content-Type': 'application/json;charset=utf-8'}
        req = request.Request(url=url, data=json.dumps(data).encode('utf-8'), headers=header,method="PUT")
        res = request.urlopen(req).read()
        return json.loads(res.decode(encoding='utf-8'))





