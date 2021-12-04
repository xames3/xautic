"""
Reloading application.

It allows live reloading of a python script. The implementation is based
on the live reloading functionality of web frameworks like Flask and
Django. Once it detects any change in the repository or the project root
files, it reloads the script.
"""

import functools
import itertools
import os
import signal
import subprocess
import sys
import threading
import time
from typing import Any
from typing import Callable
from typing import Dict
from typing import Final
from typing import Iterable
from typing import Mapping
from typing import NoReturn
from typing import Optional
from typing import Union

from ._version import __version__
from .utils import IGNORED_DIRS
from .utils import PathLike
from .utils import _all_possible_paths
from .utils import _get_args_for_reloading
from .utils import _log

try:
    import termios
except ImportError:
    termios = None  # type: ignore[assignment]

Args = Iterable
Kwargs = Mapping[str, Any]
Function = Callable[..., Any]

THREADNAME: Final[str] = "xautic-main-thread"
ENV_VAR: Final[str] = "XAUTIC_ENV"

threading.current_thread().name = THREADNAME


def _ensure_echo_on() -> None:
    """
    Ensure that echo mode is enabled. Some tools such as PDB disable it
    which causes usability issues after a reload.
    """
    if not termios or not sys.stdin.isatty():
        return
    attrs = termios.tcgetattr(sys.stdin)
    if not attrs[3] & termios.ECHO:
        attrs[3] |= termios.ECHO
        termios.tcsetattr(sys.stdin, termios.TCSANOW, attrs)


def _trigger_reload(path: PathLike) -> None:
    """Display reloading message and exit."""
    path = os.path.abspath(path)
    _log("info", f"Changes detected in {path}, refreshing script")
    sys.exit(3)


class StatReloader:
    """
    Stat based reloader.

    The reloading is triggered based on the difference of the modified
    status times of the watched files. For this, we need to know how
    many files we need to track as well as how often we should track
    them for changes. Once we have this information we can then
    calculate the modified time and later trigger the reloading.

    .. code-block:: python

        reloader = StatReloader()
        with reloader:
           reloader.run()

    .. code-block:: python

        reloader = StatReloader(interval=5.0)
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
    """

    def __init__(self, **kwargs) -> None:
        """Initialize StatReloader class with no options."""
        self.mtimes: Dict[PathLike, float] = {}
        self.track = {os.path.abspath(x) for x in kwargs.get("track") or ()}
        self.ignore_patterns = set(kwargs.get("ignore_patterns") or ())
        ignore_dirs = kwargs.get("ignore_dirs")
        if ignore_dirs:
            IGNORED_DIRS.update(ignore_dirs)
        self.interval = kwargs.get("interval", 1.0)

    def __enter__(self) -> "StatReloader":
        """
        Enter the runtime context related to this object and populate
        the initial filesystem state.
        """
        self.step_through()
        return self

    def __exit__(self, *args: Any) -> None:
        """Exit the runtime context related to this object."""

    def step_through(self) -> None:
        """
        Step through while watching the filesystem and carry on with the
        re-execution.
        """
        for path in itertools.chain(
            _all_possible_paths(self.track, self.ignore_patterns)
        ):
            try:
                curr_mtime = os.stat(path).st_mtime
            except OSError:
                continue
            prev_mtime = self.mtimes.get(path)
            if prev_mtime is None:
                self.mtimes[path] = curr_mtime
                continue
            if curr_mtime > prev_mtime:
                _trigger_reload(path)

    def run(self) -> None:
        """Continously step through and sleep after each step."""
        while 1:
            self.step_through()
            time.sleep(self.interval)


def start_xautic(
    reloader: StatReloader, func: Function, *args: Args, **kwargs: Kwargs
) -> None:
    """Start the live reloading thread."""
    _ensure_echo_on()
    xautic_main_thread = threading.Thread(
        target=func, args=args, kwargs=kwargs, name=THREADNAME
    )
    xautic_main_thread.daemon = True
    # Enter the reloader to set up an initial state, then start the main
    # thread and let the reloader update loop.
    with reloader:
        xautic_main_thread.start()
        reloader.run()


def restart_with_reloader() -> Union[NoReturn, int]:
    """
    Restart the execution in a new Python interpreter with same
    arguments.
    """
    args = _get_args_for_reloading()
    if not os.getenv(ENV_VAR):
        _log(
            "info",
            "No debugging environment found, "
            f"setting up a new environment: {ENV_VAR}",
        )
    new_environ = {**os.environ, ENV_VAR: "debug"}
    while 1:
        exit_code = subprocess.call(args, env=new_environ, close_fds=False)
        if exit_code != 3:
            return exit_code


def run_with_reloader(
    func: Optional[Function],
    *args: Args,
    track: Iterable[PathLike] = None,
    ignore_patterns: Iterable[str] = None,
    ignore_dirs: Iterable[PathLike] = None,
    interval: Union[float, int] = 1.0,
    **kwargs: Kwargs,
) -> None:
    """Run the function in an independent Python interpreter."""
    if not func:
        return
    signal.signal(signal.SIGTERM, lambda *args: sys.exit(0))
    now = time.strftime("%a %B %d, %Y - %X", time.localtime())
    script = func.__code__.co_filename
    try:
        if os.environ.get(ENV_VAR) == "debug":
            # Adding named arguments instead of kwargs to avoid conflict
            # when using or parsing the kwargs from the target function.
            reloader = StatReloader(
                track=track,
                ignore_patterns=ignore_patterns,
                ignore_dirs=ignore_dirs,
                interval=interval,
            )
            start_xautic(reloader, func, *args, **kwargs)
        else:
            _log(
                "info",
                f"Starting xautic v{__version__} live reloading "
                f"({script}) on {now}, press CTRL+C to quit",
            )
            sys.exit(restart_with_reloader())
    except KeyboardInterrupt:
        pass


def debug(
    func: Optional[Function] = None,
    track: Iterable[PathLike] = None,
    ignore_patterns: Iterable[str] = None,
    ignore_dirs: Iterable[PathLike] = None,
    interval: Union[float, int] = 1.0,
) -> Function:
    """
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
    """
    if func is None:
        return functools.partial(
            debug,
            track=track,
            ignore_patterns=ignore_patterns,
            ignore_dirs=ignore_dirs,
            interval=interval,
        )

    @functools.wraps(func)
    def inner(*args: Args, **kwargs: Kwargs) -> None:
        return run_with_reloader(
            func,
            *args,
            track=track,
            ignore_patterns=ignore_patterns,
            ignore_dirs=ignore_dirs,
            interval=interval,
            **kwargs,
        )

    return inner
