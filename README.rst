.. image:: https://img.shields.io/pypi/v/wolframalpha.svg
   :target: `PyPI link`_

.. image:: https://img.shields.io/pypi/pyversions/wolframalpha.svg
   :target: `PyPI link`_

.. _PyPI link: https://pypi.org/project/wolframalpha

.. image:: https://github.com/jaraco/wolframalpha/workflows/Automated%20Tests/badge.svg
   :target: https://github.com/jaraco/wolframalpha/actions?query=workflow%3A%22Automated+Tests%22
   :alt: Automated Tests

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/psf/black
   :alt: Code style: Black

.. image:: https://readthedocs.org/projects/wolframalpha/badge/?version=latest
   :target: https://wolframalpha.readthedocs.io/en/latest/?badge=latest

Python Client built against the `Wolfram|Alpha <http://wolframalpha.com>`_
v2.0 API.

Usage
=====

Basic usage is pretty simple. Create the client with your App ID (request from
Wolfram Alpha)::

    import wolframalpha
    app_id = 'ABC-123'  # get your own at https://products.wolframalpha.com/api/
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
            print(sub.plainText)

You may also query for simply the pods which have 'Result' titles or are
marked as 'primary' using ``Result.results``::

    print(next(res.results).plainText)

All objects returned are dictionary subclasses, so to find out which attributes
Wolfram|Alpha has supplied, simply invoke ``.keys()`` on the object.
Attributes formed from XML attributes can be accessed with or without their
"@" prefix (added by xmltodict).

For more information, read the source.
