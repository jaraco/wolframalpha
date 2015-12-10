# -*- coding: utf-8 -*-
from pmxbot.core import command

import wolframalpha

@command("wolframalpha", aliases=('wa',), doc="Wolfram Alpha rules")
def wa(client, event, channel, nick, rest):
	client = wolframalpha.Client('Q59EW4-UEL27J79UK')
	res = client.query(rest)
	return next(res.results).text
