# -*- coding: utf-8 -*-
from __future__ import absolute_import

import pmxbot
from pmxbot.core import command

import wolframalpha

@command("wolframalpha", aliases=('wa',), doc="Wolfram Alpha rules")
def wa(client, event, channel, nick, rest):
	client = wolframalpha.Client(pmxbot.config['Wolfram|Alpha API key'])
	res = client.query(rest)
	return next(res.results).text
