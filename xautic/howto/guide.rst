Quickstart
==========

This guide provides with all the help you need to install or update xautic.

Installation
^^^^^^^^^^^^

Install or upgrade Python
-------------------------

Prior to installing xautic, please ensure you have installed Python 3.6 or
later. Support for Python 2.7 and Python 3.5 earlier is deprecated. For more
information about how to get the latest version of Python, see the
official `Python documentation <https://www.python.org/downloads/>`_. To check
the current Python version use:

.. code-block:: console

    $ python --version

Install xautic
--------------

Install the latest xautic stable release via :command:`pip`:

.. code-block:: console

    $ pip install -U xautic

.. note::

   The latest development version of xautic is on `GitHub
   <https://github.com/xames3/xautic>`_.

To install the development release from GitHub:

.. code-block:: console

    $ git clone https://github.com/xames3/xautic.git
    $ cd xautic/
    $ pip install -e .

Using xautic
^^^^^^^^^^^^

To use xautic, you must first import it and use the necessary public APIs that
you need:

.. code-block:: python

    import xautic

    # Create a reloader object
    reloader = xautic.StatReloader()

    with reloader:
        reloader.run()
