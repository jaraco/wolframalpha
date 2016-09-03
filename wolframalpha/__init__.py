import itertools

from six.moves import urllib, map

import xmltodict

from . import compat

compat.fix_HTTPMessage()


class Client(object):
    """
    Wolfram|Alpha v2.0 client

    Pass an ID to the object upon instantiation, then
    query Wolfram Alpha using the query method.
    """
    def __init__(self, app_id):
        self.app_id = app_id

    def query(self, input, params=(), **kwargs):
        """
        Query Wolfram|Alpha using the v2.0 API

        Allows for arbitrary parameters to be passed in
        the query. For example, to pass assumptions:

            client.query(input='pi', assumption='*C.pi-_*NamedConstant-')

        To pass multiple assumptions, pass multiple items
        as params:

            params = (
                ('assumption', '*C.pi-_*NamedConstant-'),
                ('assumption', 'DateOrder_**Day.Month.Year--'),
            )
            client.query(input='pi', params=params)

        For more details on Assumptions, see
        https://products.wolframalpha.com/api/documentation.html#6
        """
        data = dict(
            input=input,
            appid=self.app_id,
        )
        data = itertools.chain(params, data.items(), kwargs.items())

        query = urllib.parse.urlencode(tuple(data))
        url = 'https://api.wolframalpha.com/v2/query?' + query
        resp = urllib.request.urlopen(url)
        assert resp.headers.get_content_type() == 'text/xml'
        assert resp.headers.get_param('charset') == 'utf-8'
        return Result(resp)


class ErrorHandler(object):
    @staticmethod
    def _handle_error(resp):
        error = resp.get('error')
        if not error:
            return

        code = error['code']
        msg = error['msg']
        template = 'Error {code}: {msg}'
        raise Exception(template.format(code=code, msg=msg))


class Result(ErrorHandler, object):
    """
    Handles processing the response for the programmer.
    """
    def __init__(self, stream):
        self.tree = xmltodict.parse(stream, dict_constructor=dict)['queryresult']
        self._handle_error(self.tree)
        self.info = []
        try:
            self.pods = list(map(Pod, self.tree['pod']))
            self.info.append(self.pods)
        except KeyError:
            self.pods = None
        try:
            self.assumptions = list(map(Assumption, self.tree['assumptions']))
            self.info.append(self.assumptions)
        except KeyError:
            self.assumptions = None
        try:
            self.warnings = list(map(Warning, self.tree['warnings']))
            self.info.append(self.warnings)
        except KeyError:
            self.warnings = None

    def __iter__(self):
        return iter(self.info)

    def __len__(self):
        return len(self.info)

    @property
    def results(self):
        """
        The pods that hold the response to a simple, discrete query.
        """
        return (pod for pod in self.pods if pod.primary or pod.title=='Result')

    @property
    def details(self):
        """
        A simplified set of answer text by title.
        """
        return {pod.title: pod.text for pod in self.pods}


class Pod(ErrorHandler, object):
    """
    Groups answers and information contextualizing those answers.
    """
    def __init__(self, node):
        self.node = node
        self.error = node['@error']
        self._handle_error(self.node)
        self.title = node['@title']
        self.scanner = node['@scanner']
        self.id = node['@id']
        self.position = float(node['@position'])
        self.number_of_subpods = int(node['@numsubpods'])
        self.subpods = node['subpod']
        # Allow subpods to be accessed in a consistent way,
        # as a list, regardless of how many there are.
        if type(self.subpods) != list:
            self.subpods = [self.subpods]
        self.subpods = list(map(Subpod, self.subpods))
        self.primary = '@primary' in node and node['@primary'] != 'false'

    def __iter__(self):
        return iter(self.subpods)

    def __len__(self):
        return self.number_of_subpods

    @property
    def texts(self):
        """
        The text from each subpod in this pod as a list.
        """
        return [subpod.text for subpod in self.subpods]

    @property
    def text(self):
        return next(iter(self)).text


class Subpod(object):
    """
    Holds a specific answer or additional information relevant to said answer.
    """
    def __init__(self, node):
        self.node = node
        self.title = node['@title']
        self.text = node['plaintext']
        self.img = node['img']
        # Allow images to be accessed in a consistent way,
        # as a list, regardless of how many there are.
        if type(self.img) != list:
            self.img = [self.img]
        self.img = list(map(Image, self.img))


# Needs work. At the moment this should be considered a placeholder.
class Assumption(object):
    def __init__(self, node):
        self.assumption = node
        #self.description = self.assumption[0]['desc'] # We only care about our given assumption.

    def __iter__(self):
        return iter(self.assumption)

    def __len__(self):
        return len(self.assumption)

    @property
    def text(self):
        text = self.template.replace('${desc1}', self.description)
        try:
            text = text.replace('${word}', self.word)
        except:
            pass
        return text[:text.index('. ') + 1]


# Needs work. At the moment this should be considered a placeholder.
class Warning(object):
    def __init__(self, node):
        self.node = node

    def __iter__(self):
        return iter(node)

    def __len__(self):
        return len(node)


class Image(object):
    """
    Holds information about an image included with an answer.
    """
    def __init__(self, node):
        self.node = node
        self.title = node['@title']
        self.alt = node['@alt']
        self.height = node['@height']
        self.width  = node['@width']
        self.src = node['@src']

