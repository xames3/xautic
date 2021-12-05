xautic
======

Live reloading with Python!

According to `this <https://stackoverflow.com/a/41429055/14316408/>`_ widely
accepted StackOverflow answer, Live reloading reloads or refreshes the entire
app when a file changes. For example, if you were four links deep into your
navigation and saved a change, live reloading would restart the app and load
the app back to the initial route. And that's what this module does!

The inspiration behind writing this module comes the python based web
frameworks, `Flask <https://flask.palletsprojects.com/en/2.0.x/>`_ and
`Django <https://www.djangoproject.com/>`_. These beast of a packages provide
not only the best and easiest public APIs for creating and deploying websites
but also provide one nifty feature of **live reloading**. The feature is
subtle but effective and mostly productive. Ability to quickly reload and
execute the code comes handy when you are trying to meet the deadlines. One
just needs to write, modify and save files as they wish and voila! You have
the latest execution.

The usage of this module is as simple and intuitive as it gets. Just slap a
decorator on your target function and let `xautic` do its work.

Installation
------------

Prior to installing xautic, please ensure you have installed Python 3.6 or
later. Support for Python 2.7 and Python 3.5 earlier is deprecated. For more
information about how to get the latest version of Python, see the
official `Python documentation <https://www.python.org/downloads/>`_. To check
the current Python version use:

.. code-block:: console

    $ python --version

Install and update xautic stable release using
`pip <https://pip.pypa.io/en/stable/getting-started/>`_:

.. code-block:: console

    $ pip install -U xautic

To install the development version of xautic, clone the repository:

.. code-block:: console

    $ git clone https://github.com/xames3/xautic.git
    $ cd xautic/
    $ pip install -e .

Example
-------

.. code-block:: python

    # Save this file as example.py
    from xautic import debug

    @debug
    def func():
        return "Hello World"

.. code-block:: console

    $ python3 example.py
    Starting xautic v1.0.1 live reloading (/home/example.py) on Thu May 04, 2021 - 13:23:00, press CTRL+C to quit

In Action
---------

.. image:: https://raw.githubusercontent.com/xames3/xautic/assets/media/xautic_in_action.gif
