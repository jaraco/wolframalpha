wolframalpha
============

Python Client built against the `Wolfram|Alpha <http://wolframalpha.com>`_
v2.0 API. This project is hosted on `Github
<https://github.com/jaraco/wolframalpha>`_.

Installation
============

This library is released to PyPI - the Python Package Index, so the easiest way to install it is to use
pip::

    pip install wolframalpha

or easy_install::

    easy_install wolframalpha

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

Result objects have `pods` (a Pod is an answer group from Wolfram Alpha)::

    for pod in res.pods:
        do_something_with(pod)

Pod objects have `subpods` (a Subpod is a specific response with the plaintext reply and some additional info)::
    
    for pod in res.pods:
        for sub in pod:
            print(sub.text)

You may also query for simply the pods which have 'Result' titles or are marked as 'primary'::

    print(res.results[0])

For more information, read the source.
