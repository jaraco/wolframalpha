import itertools
import json

from six.moves import urllib, map

import xmltodict
from jaraco.itertools import always_iterable

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
    def __init__(self, *args, **kwargs):
        super(ErrorHandler, self).__init__(*args, **kwargs)
        self._handle_error()

    def _handle_error(self):
        if 'error' not in self:
            return

        template = 'Error {error[code]}: {error[msg]}'
        raise Exception(template.format(**self))


class Document(dict):
    _attr_types = {}
    "Override the types from the document"

    @classmethod
    def from_doc(cls, doc):
        """
        Load instances from the xmltodict result. Always return
        an iterable, even if the result is a singleton.
        """
        return map(cls, always_iterable(doc))

    def __getattr__(self, name):
        type = self._attr_types.get(name, lambda x: x)
        attr_name = '@' + name
        try:
            val = self[name] if name in self else self[attr_name]
        except KeyError:
            raise AttributeError(name)
        return type(val)


class Assumption(Document):
    @property
    def text(self):
        text = self.template.replace('${desc1}', self.description)
        try:
            text = text.replace('${word}', self.word)
        except Exception:
            pass
        return text[:text.index('. ') + 1]


class Warning(Document):
    pass


class Image(Document):
    """
    Holds information about an image included with an answer.
    """
    _attr_types = dict(
        height=int,
        width=int,
    )


class Subpod(Document):
    """
    Holds a specific answer or additional information relevant to said answer.
    """
    _attr_types = dict(
        img=Image.from_doc,
    )


def xml_bool(str_val):
    """
    >>> xml_bool('true')
    True
    >>> xml_bool('false')
    False
    """
    return bool(json.loads(str_val))


class Pod(ErrorHandler, Document):
    """
    Groups answers and information contextualizing those answers.
    """
    _attr_types = dict(
        position=float,
        numsubpods=int,
        subpod=Subpod.from_doc,
    )

    @property
    def subpods(self):
        return self.subpod

    @property
    def primary(self):
        return '@primary' in self and xml_bool(self['@primary'])

    @property
    def texts(self):
        """
        The text from each subpod in this pod as a list.
        """
        return [subpod.plaintext for subpod in self.subpod]

    @property
    def text(self):
        return next(iter(self.subpod)).plaintext


class Result(ErrorHandler, Document):
    """
    Handles processing the response for the programmer.
    """
    _attr_types = dict(
        pod=Pod.from_doc,
    )

    def __init__(self, stream):
        doc = xmltodict.parse(stream, dict_constructor=dict)['queryresult']
        super(Result, self).__init__(doc)

    @property
    def info(self):
        """
        The pods, assumptions, and warnings of this result.
        """
        return itertools.chain(self.pods, self.assumptions, self.warnings)

    @property
    def pods(self):
        return self.pod

    @property
    def assumptions(self):
        return Assumption.from_doc(self.get('assumptions'))

    @property
    def warnings(self):
        return Warning.from_doc(self.get('warnings'))

    def __iter__(self):
        return self.info

    def __len__(self):
        return sum(1 for _ in self.info)

    @property
    def results(self):
        """
        The pods that hold the response to a simple, discrete query.
        """
        return (
            pod
            for pod in self.pods
            if pod.primary
            or pod.title == 'Result'
        )

    @property
    def details(self):
        """
        A simplified set of answer text by title.
        """
        return {pod.title: pod.text for pod in self.pods}
