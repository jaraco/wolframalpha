import pmxbot
from pmxbot.core import command

import wolframalpha


@command(aliases='wolframalpha')
def wa(client, event, channel, nick, rest):
    """
    A free-text query resolver by Wolfram|Alpha. Returns the first
    result, if available.
    """
    client = wolframalpha.Client(pmxbot.config['Wolfram|Alpha API key'])
    res = client.query(rest)
    return next(res.results).plainText
