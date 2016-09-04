import os

import six

import pytest

import wolframalpha


if six.PY2:
    collect_ignore = [
    	'wolframalpha/pmxbot.py',
    	'wolframalpha/test_pmxbot.py',
    ]


@pytest.fixture(scope='session')
def API_key():
	"""
	To run the tests fully, the environment must be configured
	with a WOLFRAMALPHA_API_KEY environment variable. Otherwise,
	skip them.
	"""
	try:
		return os.environ['WOLFRAMALPHA_API_KEY']
	except KeyError:
		pytest.skip("Need WOLFRAMALPHA_API_KEY in environment")


@pytest.fixture(scope='session')
def client(API_key):
	return wolframalpha.Client(API_key)
