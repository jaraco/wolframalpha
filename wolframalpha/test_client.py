#-*- coding: utf-8 -*-

from __future__ import unicode_literals

import os

import pytest

import wolframalpha


@pytest.fixture
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


def test_basic(API_key):
	client = wolframalpha.Client(API_key)
	res = client.query('30 deg C in deg F')
	assert len(res.pods) > 0
	results = list(res.results)
	assert results[0].text == '86 °F  (degrees Fahrenheit)'

def test_invalid_app_id():
	client = wolframalpha.Client('abcdefg')
	with pytest.raises(Exception):
		client.query('30 deg C in deg F')
