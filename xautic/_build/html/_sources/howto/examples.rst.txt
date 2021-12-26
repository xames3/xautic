Usage examples
==============

This section provides with the code examples that demonstrate how to use the
xautic for Python to live reload your code.

Prerequisite tasks
^^^^^^^^^^^^^^^^^^

To set up and run this example, you must first have a proper Python 3.6
installation as described in :doc:`guide`.

Examples
^^^^^^^^

Live reloading
--------------

The below example shows how to debug or live reload your function or script
using xautic. This setup, without any arguments to the `debug` decorator just
tracks the project root and only the Python files in it.

.. code-block:: python

    import xautic

    @xautic.debug
    def func(*args, **kwargs):
        ...

Tracking non-pythonic files
---------------------------

The below example shows how to track non-python files as well for live
reloading. This will ensure all the changes happening in these files are also
tracked while the debugging environment is active.

.. code-block:: python

    import xautic

    @xautic.debug(track=["/home/.bashrc", "/home/.bash_profile"])
    def func(*args, **kwargs):
        ...

Ignoring files and directories based on RegEx
---------------------------------------------

The below example shows how to ignore tracking of the files and directories
based on their `regex <https://en.wikipedia.org/wiki/Regular_expression>`_
pattern. This is a helpful and nifty trick when you want to reduce the CPU
utilization.

.. code-block:: python

    import xautic

    @xautic.debug(ignore_patterns=["*.js", ".log"])
    def func(*args, **kwargs):
        ...

Doing this will make xautic ignore all the files ending with `.js` and `.log`
extensions.

.. code-block:: python

    import xautic

    @xautic.debug(ignore_patterns=[r"**/[^_]static/"])
    def func(*args, **kwargs):
        ...

This will make xautic ignore all the files under the `_static` directory.
