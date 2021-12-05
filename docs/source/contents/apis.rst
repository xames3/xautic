API References
==============

.. class:: StatReloader(**kwargs)

    Stat based reloader.

    The reloading is triggered based on the difference of the modified
    status times of the watched files. For this, we need to know how
    many files we need to track as well as how often we should track
    them for changes. Once we have this information we can then
    calculate the modified time and later trigger the reloading.

    :Examples:

        .. code-block:: python

            reloader = StatReloader(interval=5.0)
            reloader.run()

        .. code-block:: python

            # Create a reloader context instance
            reloader = StatReloader()

            with reloader:
                reloader.run()

    .. note::
        The current implementation is based on the stat based changes
        detected by the :py:func:`~os.stat`. This can be further
        improved using the `watchdog.observer`. But it seems that it
        increases the overhead. Whereas this implementation is minimal
        and roughly works the same.

    .. versionchanged:: 1.0.0
        In previous development version "track", "ignore_patterns" and
        "ignore_dirs" were used as means of named arguments for
        controlling the behavior of the :py:class:`StatReloader`. Now
        added support for kwargs instead.

.. method:: restart_with_reloader() -> Union[NoReturn, int]

    Restart the execution in a new Python interpreter with same
    arguments.

.. method:: run_with_reloader(func: Callable[..., Any] = None, *args: Iterable[Any], track: Optional[Iterable[PathLike]] = None, ignore_patterns: Optional[Iterable[str]] = None, ignore_dirs: Optional[Iterable[PathLike]] = None, interval: Union[float, int] = 1.0, **kwargs: Mapping[str, Any]) -> None

    Run the function in an independent Python interpreter.

.. method:: debug(func: Optional[Callable[..., Any]] = None, track: Optional[Iterable[PathLike]] = None, ignore_patterns: Optional[Iterable[str]] = None, ignore_dirs: Optional[Iterable[PathLike]] = None, interval: Union[float, int] = 1.0) -> Callable[..., Any]

    Live debugging decorator.

    Decorate function that needs to be reloaded on change. This function
    internally calls :py:func:`run_with_reloader`.

    :param func: Function to run with live reloading.
    :param track: Iterable of absolute paths of both python & non-python
        files to track. Defaults to None.
    :param ignore_patterns: Iterable of path patterns to ignore. The
        patterns can be regular expressions or just names of the file(s)
        and directories to be ignored. Defaults to None.
    :param ignore_dirs: Directories to skip while watching. This does
        not expect the full absolute path of the directories, only the
        directory names will do. Defaults to None.
    :param interval: Seconds to sleep between reloading. The less the
        duration, more aggressively it will track for changes. Defaults
        to 1.0 sec.

    :Examples:

        .. code-block:: python

            @debug
            def func(*args, **kwargs):
                ...

        .. code-block:: python

            @debug(track=["/home/.bashrc", "/home/.bash_profile"])
            def func(*args, **kwargs):
                ...

    .. note::
        Well, you can add non-python files to track but doing so might
        increase the CPU utilization. It is more advisable to track only
        python files e.g. py, pyc or pyw.
