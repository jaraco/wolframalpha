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
        self._doc = xmltodict.parse(stream, dict_constructor=dict)['queryresult']
        self._handle_error(self._doc)

    @property
    def info(self):
        """
        The pods, assumptions, and warnings of this result.
        """
        return itertools.chain(self.pods, self.assumptions, self.warnings)

    @property
    def pods(self):
        return map(Pod, self._doc.get('pod', []))

    @property
    def assumptions(self):
        return map(Assumption, self._doc.get('assumptions', []))

    @property
    def warnings(self):
        return map(Warning, self._doc.get('warnings', []))

    def __iter__(self):
        return self.info

    def __len__(self):
        return sum(1 for _ in self.info)

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
    def __init__(self, doc):
        self._doc = doc
        self.error = doc['@error']
        self._handle_error(doc)
        self.title = doc['@title']
        self.scanner = doc['@scanner']
        self.id = doc['@id']
        self.position = float(doc['@position'])
        self.number_of_subpods = int(doc['@numsubpods'])
        self.subpods = doc['subpod']
        # Allow subpods to be accessed in a consistent way,
        # as a list, regardless of how many there are.
        if type(self.subpods) != list:
            self.subpods = [self.subpods]
        self.subpods = list(map(Subpod, self.subpods))
        self.primary = '@primary' in doc and doc['@primary'] != 'false'

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
    def __init__(self, doc):
        self._doc = doc
        self.title = doc['@title']
        self.text = doc['plaintext']
        self.img = doc['img']
        # Allow images to be accessed in a consistent way,
        # as a list, regardless of how many there are.
        if type(self.img) != list:
            self.img = [self.img]
        self.img = list(map(Image, self.img))


# Needs work. At the moment this should be considered a placeholder.
class Assumption(object):
    def __init__(self, doc):
        self._doc = doc
        #self.description = self._doc[0]['desc'] # We only care about our given assumption.

    def __iter__(self):
        return iter(self._doc)

    def __len__(self):
        return len(self._doc)

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
    def __init__(self, doc):
        self._doc = doc

    def __iter__(self):
        return iter(self._doc)

    def __len__(self):
        return len(self._doc)


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

