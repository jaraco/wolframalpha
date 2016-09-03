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


@pytest.fixture
def client(API_key):
	return wolframalpha.Client(API_key)

def test_basic(client):
	res = client.query('30 deg C in deg F')
	assert len(res.pods) > 0
	result, = res.results
	assert result.text == '86 °F  (degrees Fahrenheit)'
	assert result.texts == ['86 °F  (degrees Fahrenheit)']


def test_results_iterator(client):
	"""
	A Result.results should be an iterator.
	"""
	res = client.query('30 deg C in deg F')
	next(res.results)


def test_invalid_app_id():
	client = wolframalpha.Client('abcdefg')
	with pytest.raises(Exception):
		client.query('30 deg C in deg F')
