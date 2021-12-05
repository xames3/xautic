.. xautic documentation master file, created by
   sphinx-quickstart on Sun Dec  5 17:34:36 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

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

Quickstart
----------

.. toctree::
   :maxdepth: 3

   contents/guide
   contents/examples

API reference
-------------

.. toctree::
   :maxdepth: 2

   contents/apis

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
