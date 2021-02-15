import pytest

import wolframalpha


@pytest.fixture(scope='module')
def temp_result(client):
    return client.query('30 deg C in deg F')


def test_basic(temp_result):
    res = temp_result
    assert temp_result.success
    assert len(list(res.pods)) > 0
    (result,) = res.results
    assert result.text == '86 °F (degrees Fahrenheit)'
    assert result.texts == ['86 °F (degrees Fahrenheit)']


def test_results_iterator(temp_result):
    """
    A Result.results should be an iterator.
    """
    res = temp_result
    next(res.results)


def test_result_details(temp_result):
    assert temp_result.details


def test_properties(temp_result):
    """
    A result should have a number of properties.
    """
    res = temp_result
    info = list(res.info)
    warnings = list(res.warnings)
    assert all(isinstance(item, wolframalpha.Warning) for item in warnings)
    assumptions = list(res.assumptions)
    assert all(isinstance(item, wolframalpha.Assumption) for item in assumptions)
    pods = list(res.pods)
    assert all(isinstance(item, wolframalpha.Pod) for item in pods)
    assert len(info) == len(pods) + len(warnings) + len(assumptions)


def test_pod_attributes(temp_result):
    pod = next(temp_result.pods)
    assert isinstance(pod.position, float)
    assert isinstance(pod.id, str)
    img = next(iter(pod.subpods)).img
    assert isinstance(img.height, int)


def test_invalid_app_id():
    client = wolframalpha.Client('abcdefg')
    with pytest.raises(Exception):
        client.query('30 deg C in deg F')


def test_unsuccessful(client):
    """
    A result for an unsuccessful query should be False and
    have empty info.
    """
    res = client.query('this is a sentence')
    assert not res.success
    assert not res
    assert len(res) == 0
    assert list(res.info) == []


def test_from_env(monkeypatch):
    monkeypatch.delenv('WOLFRAMALPHA_API_KEY', raising=False)
    with pytest.raises(KeyError):
        wolframalpha.Client._from_env()


class TestDocument:
    def test_missing_attr(self):
        doc = wolframalpha.Document()
        with pytest.raises(AttributeError):
            doc.missing


class TestAssumption:
    def test_text(self):
        doc = wolframalpha.Assumption(
            template='Assume ${desc1} and ${word}. Nothing more.',
            description='description',
            word='word',
        )
        assert doc.text == 'Assume description and word.'
