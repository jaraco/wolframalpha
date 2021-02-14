import pytest

import wolframalpha


@pytest.fixture(scope='session')
def API_key(client):
    return client.app_id


@pytest.fixture(scope='session')
def client():
    try:
        return wolframalpha.Client.from_env()
    except Exception:  # pragma: nocover
        pytest.skip("Need WOLFRAMALPHA_API_KEY in environment")
