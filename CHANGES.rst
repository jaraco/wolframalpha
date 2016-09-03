3.0
===

* Models now parse the results using xmltodict.
* Changed parameter of ``Client.query`` from
  ``query`` to ``input``.
* ``Client.query`` now accepts keyword arguments
  and parameters passed directly to Wolfram|Alpha
  as URL parameters.
* ``Result.pods`` and ``Pod.subpods`` now returns
  an iterator and not a list.
* ``Pod`` objects are no longer iterable. To access
  the subpods of a pod, simply use the ``Pod.subpod``
  property.
* ``Result.tree`` and ``Pod.node`` have been removed.
* ``Result`` now additionally presents the new attributes:
    - assumptions: An iterable of Assumptions.
    - warnings: An iterable of Warnings.
    - info: An iterable combining all Pods, Assumptions,
      and Warnings.

2.4
===

Automated release process with Travis-CI.

Issue #5: Use HTTPS by default.

2.3
===

Moved hosting to Github.

2.2
===

Add support for images (img attribute on Atom).

2.0
===

``pmxbot`` plugin now requires that the "Wolfram|Alpha API key"
config parameter be supplied. The hard-coded key has been
removed and will be de-activated. Users must register for their
own key at the `Wolfram|Alpha developer web site
<https://developer.wolframalpha.com>`_.

Additionally, the tests now no longer bundle a hard-coded API
key. Instead, to run the tests, one must supply a
``WOLFRAMALPHA_API_KEY`` environment variable.

1.4
===

Add pmxbot module and plugin, superseding pmxbot-wolframalpha package.

1.3
===

Moved hosting to Github.
