"""
Reloading application.

It allows live reloading of a python script. The implementation is based
on the live reloading functionality of web frameworks like Flask and
Django. Once it detects any change in the repository or the project root
files, it reloads the script.
"""

import itertools
import os
import signal
import subprocess
import sys
import threading
import time
import typing as t

from ._version import __version__
from .utils import IGNORED_DIRS
from .utils import PathLike
from .utils import _all_possible_paths
from .utils import _get_args_for_reloading
from .utils import log

try:
    import termios
except ImportError:
    termios = None  # type: ignore[assignment]

THREADNAME: t.Final[str] = "xautic-main-thread"
ENV_VAR: t.Final[str] = "XAUTIC_ENV"

threading.current_thread().name = THREADNAME


def _trigger_reload(path: PathLike) -> None:
    """Display reloading message and exit."""
    path = os.path.abspath(path)
    log("info", f"Changes detected in {path}, refreshing script")
    sys.exit(3)


def restart_with_reloader() -> t.Union[int, t.NoReturn]:
    """
    Restart the execution in a new Python interpreter with same
    arguments.
    """
    args = _get_args_for_reloading()
    if not os.getenv(ENV_VAR):
        log(
            "info",
            "No debugging environment found, setting up a new environment: "
            f"{ENV_VAR.lower()}",
        )
    new_environ = {**os.environ, ENV_VAR: "debug"}
    while 1:
        exit_code = subprocess.call(args, env=new_environ, close_fds=False)
        if exit_code != 3:
            return exit_code


class StatReloader:
    """
    Stat based reloader.

    The reloading is triggered based on the difference of the modified
    status times of the watched files. For this, we need to know how
    many files we need to track as well as how often we should track
    them for changes. Once we have this information we can then
    calculate the modified time and later trigger the reloading.

    :param track: Absolute paths of both python & non-python files to
        track. Well, you can add non-python files to track but doing
        so might increase the CPU utilization. It is more advisable to
        track only python files e.g.: .py or .pyc. Defaults to None.
    :param ignore_patterns: Path patterns to ignore. The patterns can be
        regular expressions or just names of the file(s) and directories
        to be ignored. Defaults to None.
    :param ignore_dirs: Directories to skip while watching. This does
        not expect the full absolute path of the directories, only the
        directory names will do. Defaults to None.
    :param interval: Seconds to sleep between reloading. The less the
        duration, more aggressively it will track for changes. Defaults
        to 1.0 sec.

    .. code-block:: python

        >>> reloader = StatReloader()
        >>> with reloader:
        ...    reloader.run()

    .. note::

        The current implementation is based on the stat based changes
        detected by the :py:func:`~os.stat`. This can be further
        improved using the `watchdog.observer`. But it seems that it
        increases the overhead. Whereas this implementation is minimal
        and roughly works the same.
    """

    def __init__(
        self,
        track: t.Optional[t.Iterable[PathLike]] = None,
        ignore_patterns: t.Optional[t.Iterable[str]] = None,
        ignore_dirs: t.Optional[t.Iterable[PathLike]] = None,
        interval: t.Union[int, float] = 1.0,
    ) -> None:
        """Initialize StatReloader class with no options."""
        self.mtimes: t.Dict[PathLike, float] = {}
        self.track = {os.path.abspath(x) for x in track or ()}
        self.ignore_patterns = set(ignore_patterns or ())
        if ignore_dirs:
            IGNORED_DIRS.update(ignore_dirs)
        self.interval = interval

    def __enter__(self) -> "StatReloader":
        """
        Enter the runtime context related to this object and populate
        the initial filesystem state.
        """
        self.step_through()
        return self

    def __exit__(self, *args) -> None:
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


def ensure_echo_on() -> None:
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


def run_with_reloader(
    func: t.Callable[[t.Any], t.Any],
    *args: t.Any,
    track: t.Optional[t.Iterable[PathLike]] = None,
    ignore_patterns: t.Optional[t.Iterable[str]] = None,
    ignore_dirs: t.Optional[t.Iterable[PathLike]] = None,
    interval: t.Union[int, float] = 1.0,
    **kwargs: t.Any,
) -> None:
    """
    Run the function in an independent Python interpreter.

    :param func: Function to be called with live reloading.
    :param track: Absolute paths of both python & non-python files to
        track. Well, you can add non-python files to track but doing
        so might increase the CPU utilization. It is more advisable to
        track only python files e.g.: .py or .pyc. Defaults to None.
    :param ignore_patterns: Path patterns to ignore. The patterns can be
        regular expressions or just names of the file(s) and directories
        to be ignored. Defaults to None.
    :param ignore_dirs: Directories to skip while watching. This does
        not expect the full absolute path of the directories, only the
        directory names will do. Defaults to None.
    :param interval: Seconds to sleep between reloading. The less the
        duration, more aggressively it will track for changes. Defaults
        to 1.0 sec.

    .. code-block:: python

        >>> def func(*args, **kwargs):
        ...     pass
        ...
        >>> run_with_reloader(func, *args, **kwargs)

    """
    signal.signal(signal.SIGTERM, lambda *args: sys.exit(0))
    now = time.strftime("%a %B %d, %Y - %X", time.localtime())
    script = func.__code__.co_filename
    quit_cmd = "CTRL+BREAK" if sys.platform == "win32" else "CTRL+C"
    reloader = StatReloader(track, ignore_patterns, ignore_dirs, interval)
    try:
        if os.environ.get(ENV_VAR) == "debug":
            ensure_echo_on()
            xautic_main_thread = threading.Thread(
                name=THREADNAME,
                target=func,
                args=args,
                kwargs=kwargs,
            )
            xautic_main_thread.daemon = True
            with reloader:
                xautic_main_thread.start()
                reloader.run()
        else:
            log(
                "info",
                f"Starting live reloading v{__version__} ({script}) "
                f"on {now}, press {quit_cmd} to quit",
            )
            sys.exit(restart_with_reloader())
    except KeyboardInterrupt:
        pass
