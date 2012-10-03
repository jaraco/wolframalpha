import urllib
import urllib2
from xml.etree import ElementTree as etree

class Result(object):
    def __init__(self, stream):
        self.tree = etree.parse(stream)

    @property
    def pods(self):
        return map(Pod, self.tree.findall('pod'))

class Pod(object):
    def __init__(self, node):
        self.node = node
        self.__dict__.update(node.attrib)

    def __iter__(self):
        return (Content(node) for node in self.nodes.findall('subpod'))

    @property
    def main(self):
        "The main content of this pod"
        return next(iter(self))

    @property
    def text(self):
        return self.main.text

class Content(object):
    def __init__(self, node):
        self.node = node
        self.__dict__.update(node.attrib)
        self.text = node.find('plaintext').text

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
        assert resp.headers.gettype() == 'text/xml'
        assert resp.headers.getparam('charset') == 'utf-8'
        return Result(resp)
