import pmxbot

import wolframalpha.pmxbot


def test_pmxbot_command(monkeypatch, API_key):
	config = {'Wolfram|Alpha API key': API_key}
	monkeypatch.setattr(pmxbot, 'config', config, raising=False)
	query = "1kg in lbs"
	res = wolframalpha.pmxbot.wa(None, None, None, None, rest=query)
	assert res == '2.205 lb  (pounds)'
