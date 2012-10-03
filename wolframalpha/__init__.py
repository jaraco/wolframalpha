import urllib
import urllib2
from xml.etree import ElementTree as etree

class Result(object):
    def __init__(self, stream):
        self.tree = etree.parse(stream)

class Client(object):
    """
    Wolfram|Alpha v2.0 client
    """
    def __init__(self, app_id):
        self.app_id = app_id

    def query(self, query):
        """
        Query Wolfram|Alpha with query using the v2.0 API
        """
        query = urllib.urlencode(dict(
            input=query,
            appid=self.app_id,
        ))
        url = 'http://api.wolframalpha.com/v2/query?' + query
        resp = urllib2.urlopen(url)
        assert resp.headers['Content-Type'] == 'application/xml'
        return Result(resp)
