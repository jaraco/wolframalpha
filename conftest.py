import getpass
import os

import six

import pytest
import keyring
from jaraco.context import suppress

import wolframalpha


if six.PY2:
    collect_ignore = [
        'wolframalpha/pmxbot.py',
        'wolframalpha/test_pmxbot.py',
    ]


@suppress(Exception)
def from_keyring():
    return keyring.get_password('https://api.wolframalpha.com/', getpass.getuser())


@pytest.fixture(scope='session')
def API_key():
    """
    To run the tests fully, the environment must be configured
    with a WOLFRAMALPHA_API_KEY environment variable. Otherwise,
    skip them.
    """
    try:
        return from_keyring() or os.environ['WOLFRAMALPHA_API_KEY']
    except KeyError:
        pytest.skip("Need WOLFRAMALPHA_API_KEY in environment")


@pytest.fixture(scope='session')
def client(API_key):
    return wolframalpha.Client(API_key)
