import contextlib
import importlib.util

import pytest

import wolframalpha

collect_ignore = (
    []
    if importlib.util.find_spec('pmxbot')
    else ['wolframalpha/pmxbot.py', 'tests/test_pmxbot.py']
)


@pytest.fixture(scope='session')
def API_key(client):
    return client.app_id


@pytest.fixture(scope='session')
def client():
    with contextlib.suppress(Exception):
        return wolframalpha.Client.from_env()

    pytest.skip("Need WOLFRAMALPHA_API_KEY in environment")  # pragma: nocover
