import contextlib

import pytest

import wolframalpha


@pytest.fixture(scope='session')
def API_key(client):
    return client.app_id


@pytest.fixture(scope='session')
def client():
    with contextlib.suppress(Exception):
        return wolframalpha.Client.from_env()

    pytest.skip("Need WOLFRAMALPHA_API_KEY in environment")  # pragma: nocover
