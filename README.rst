wolframalpha
============

Python Client built against the `Wolfram|Alpha <http://wolframalpha.com>`_
v2.0 API. This project is hosted on `bitbucket
<https://github.com/jaraco/wolframalpha>`_.

Installation
============

This library is released to PyPI, so the easiest way to install it is to use
easy_install::

    easy_install wolframalpha

or pip::

    pip install wolframalpha

If you don't have these tools or you prefer not to use setuptools, you may
also simply extract the 'wolframalpha' directory an appropriate location in
your Python path.

Usage
=====

Basic usage is pretty simple. Create the client with your App ID (request from
Wolfram Alpha)::

    import wolframalpha
    client = wolframalpha.Client(app_id)

Then, you can send queries, which return Result objects::

    res = client.query('temperature in Washington, DC on October 3, 2012')

Result objects have `pods` attribute (a Pod is an answer from Wolfram Alpha)::

    for pod in res.pods:
        do_something_with(pod)

You may also query for simply the pods which have 'Result' titles::

    print(next(res.results).text)

For more information, read the source.
