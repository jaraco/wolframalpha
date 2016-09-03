.. image:: https://img.shields.io/pypi/v/wolframalpha.svg
   :target: https://pypi.org/project/wolframalpha

.. image:: https://img.shields.io/pypi/pyversions/wolframalpha.svg

.. image:: https://img.shields.io/pypi/dm/wolframalpha.svg

.. image:: https://img.shields.io/travis/jaraco/wolframalpha/master.svg
   :target: http://travis-ci.org/jaraco/wolframalpha

Python Client built against the `Wolfram|Alpha <http://wolframalpha.com>`_
v2.0 API. This project is hosted on `Github
<https://github.com/jaraco/wolframalpha>`_.

Usage
=====

Basic usage is pretty simple. Create the client with your App ID (request from
Wolfram Alpha)::

    import wolframalpha
    client = wolframalpha.Client(app_id)

Then, you can send queries, which return Result objects::

    res = client.query('temperature in Washington, DC on October 3, 2012')

Result objects have `pods` (a Pod is an answer group from Wolfram Alpha)::

    for pod in res.pods:
        do_something_with(pod)

Pod objects have ``subpods`` (a Subpod is a specific response with the plaintext
reply and some additional info)::

    for pod in res.pods:
        for sub in pod.subpods:
            print(sub.text)

You may also query for simply the pods which have 'Result' titles or are
marked as 'primary' using ``Result.results``::

    print(next(res.results).text)

All objects returned are dictionary subclasses, so to find out which attributes
Wolfram|Alpha has supplied, simply invoke ``.keys()`` on the object.
Attributes formed from XML attributes can be accessed with or without their
"@" prefix (added by xmltodict).

For more information, read the source.
