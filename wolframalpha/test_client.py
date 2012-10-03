import wolframalpha

app_id = 'Q59EW4-7K8AHE858R'
"App ID for testing this project. Please don't use for other apps."

def test_basic():
	client = wolframalpha.Client(app_id)
	client.query('30 deg C in deg F')
