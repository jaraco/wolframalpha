import asyncio
import collections
import contextlib
import getpass
import itertools
import json
import os
from typing import Any, Callable, Dict, Tuple

import httpx
import multidict
import xmltodict
from jaraco.context import suppress
from more_itertools import always_iterable


def xml_bool(str_val):
    """
    >>> xml_bool('true')
    True
    >>> xml_bool('false')
    False
    """
    return bool(json.loads(str_val))


class Client:
    """
    Wolfram|Alpha v2.0 client

    Basic usage is pretty simple. Get your App ID at
    https://products.wolframalpha.com/api/.
    Create the client with your App ID:

    >>> app_id = getfixture('API_key')
    >>> client = Client(app_id)

    Send a query, which returns Results objects:

    >>> res = client.query('temperature in Washington, DC on October 3, 2012')

    Result objects have `pods` (a Pod is an answer group from Wolfram Alpha):

    >>> for pod in res.pods:
    ...     pass  # do_something_with(pod)

    Pod objects have ``subpods`` (a Subpod is a specific response
    with the plaintext reply and some additional info):

    >>> for pod in res.pods:
    ...     for sub in pod.subpods:
    ...         print(sub.plaintext)
    temperature | Washington, District of Columbia
    Wednesday, October 3, 2012
    (70 to 81) °F (average: 75 °F)
    ...

    To query simply for the pods that have 'Result' titles or are
    marked as 'primary' using ``Result.results``:

    >>> print(next(res.results).text)
    (70 to 81) °F (average: 75 °F)
    (Wednesday, October 3, 2012)

    All objects returned are dictionary subclasses, so to find out which attributes
    Wolfram|Alpha has supplied, simply invoke ``.keys()`` on the object.
    Attributes formed from XML attributes can be accessed with or without their
    "@" prefix (added by xmltodict).

    """

    url = 'https://api.wolframalpha.com/v2/query'

    def __init__(self, app_id):
        self.app_id = app_id

    @classmethod
    def from_env(cls):
        """
        Create a client with a key discovered from the keyring
        or environment variable. Raises an exception if no key
        is found.
        """
        return cls(cls._from_keyring() or cls._from_env())

    @staticmethod
    @suppress(Exception)
    def _from_keyring():
        import keyring

        return keyring.get_password('https://api.wolframalpha.com/', getpass.getuser())

    @staticmethod
    def _from_env():
        return os.environ['WOLFRAMALPHA_API_KEY']

    def query(self, input, params=(), **kwargs):
        """
        Query Wolfram|Alpha using the v2.0 API

        Allows for arbitrary parameters to be passed in
        the query. For example, to pass assumptions:

        >>> client = Client(getfixture('API_key'))
        >>> res = client.query(input='pi', assumption='*C.pi-_*NamedConstant-')

        To pass multiple assumptions, pass multiple items
        as params:

        >>> params = (
        ...     ('assumption', '*C.pi-_*NamedConstant-'),
        ...     ('assumption', 'DateOrder_**Day.Month.Year--'),
        ... )
        >>> res = client.query(input='pi', params=params)

        For more details on Assumptions, see
        https://products.wolframalpha.com/api/documentation.html#6
        """
        return asyncio.run(self.aquery(input, params, **kwargs))

    async def aquery(self, input, params=(), **kwargs):
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                self.url,
                params=multidict.MultiDict(
                    params, appid=self.app_id, input=input, **kwargs
                ),
            )
        assert resp.headers['Content-Type'] == 'text/xml;charset=utf-8'
        doc = xmltodict.parse(resp.content, postprocessor=Document.make)
        return doc['queryresult']


class ErrorHandler:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._handle_error()

    def _handle_error(self):
        if 'error' not in self:
            return

        raise ValueError('Error {error[code]}: {error[msg]}'.format_map(self))


def identity(x):
    return x


class Document(dict):
    _attr_types: Dict[str, Callable[[str], Any]] = collections.defaultdict(
        lambda: identity,
        height=int,
        width=int,
        numsubpods=int,
        position=float,
        primary=xml_bool,
        success=xml_bool,
    )
    children: Tuple[str, ...] = ()

    @classmethod
    def _find_cls(cls, key):
        """
        Find a possible class for wrapping an item by key.
        """
        matching = (
            sub
            for sub in cls.__subclasses__()
            if key == getattr(sub, 'key', sub.__name__.lower())
        )
        return next(matching, identity)

    @classmethod
    def make(cls, path, key, value):
        value = cls._find_cls(key)(value)
        value = cls._attr_types[key.lstrip('@')](value)
        return key, value

    def __getattr__(self, name):
        return self._get_children(name) or self._get_attr(name)

    def _get_attr(self, name):
        attr_name = '@' + name
        try:
            val = self[name] if name in self else self[attr_name]
        except KeyError as err:
            raise AttributeError(name) from err
        return val

    def _get_children(self, name):
        if name not in self.__class__.children:
            return

        # some objects, like Assumptions and Warnings
        # are found in a container with the plural name;
        # others like Pods and Subpods appear directly in
        # the parent (self).
        container = self.get(name, self)
        singular = name.rstrip('s')
        return always_iterable(container.get(singular), base_type=dict)


class Assumption(Document):
    @property
    def text(self):
        text = self.template.replace('${desc1}', self.description)
        with contextlib.suppress(Exception):
            text = text.replace('${word}', self.word)
        return text[: text.index('. ') + 1]


class Warning(Document):
    pass


class Image(Document):
    """
    Holds information about an image included with an answer.
    """

    key = 'img'


class Subpod(Document):
    """
    Holds a specific answer or additional information relevant to said answer.
    """


class Pod(ErrorHandler, Document):
    """
    Groups answers and information contextualizing those answers.
    """

    children = ('subpods',)

    @property
    def primary(self):
        return self.get('@primary', False)

    @property
    def texts(self):
        """
        The text from each subpod in this pod as a list.
        """
        return [subpod.plaintext for subpod in self.subpods]

    @property
    def text(self):
        return next(iter(self.subpods)).plaintext


class Result(ErrorHandler, Document):
    """
    Handles processing the response for the programmer.
    """

    key = 'queryresult'
    children = 'pods', 'assumptions', 'warnings'

    @property
    def info(self):
        """
        The pods, assumptions, and warnings of this result.
        """
        return itertools.chain(self.pods, self.assumptions, self.warnings)

    def __iter__(self):
        return self.info

    def __len__(self):
        return sum(1 for _ in self)

    def __bool__(self):
        return bool(len(self))

    @property
    def results(self):
        """
        The pods that hold the response to a simple, discrete query.
        """
        return (pod for pod in self.pods if pod.primary or pod.title == 'Result')

    @property
    def details(self):
        """
        A simplified set of answer text by title.
        """
        return {pod.title: pod.text for pod in self.pods}
