"""Useful utilities.

Utility functions that offers general convenience to facilitate live
reloading and tracking of the necessary components. Primarily these
functions are used within xautic, but they can also be used for external
consumption.
"""

import fnmatch
import itertools
import logging
import os
import sys
from typing import Any
from typing import Iterator
from typing import List
from typing import Optional
from typing import Set
from typing import Tuple
from typing import Union
from typing import cast

PathLike = Union[str, os.PathLike]

_logger: Optional[logging.Logger] = None

# These are the directories that we purposely ignore while tracking the
# changes within the working root. This optimization reduces the CPU
# utilization significantly since there will be few files to track.
IGNORED_DIRS: Set[PathLike] = {
    ".egg-info",
    ".git",
    ".hg",
    ".mypy_cache",
    ".pytest_cache",
    "__pycache__",
}
VALID_PY_FILES: Tuple[str, ...] = (".py", ".pyc", ".pyw")

# All possible system prefixes from where the imports can be found. The
# base values are different when running from a virtualenv. The reloader
# won't scan these directories as it would be too inefficient.
prefixes: Union[Set[PathLike], Tuple[PathLike, ...]] = {
    sys.prefix,
    sys.base_prefix,
    sys.exec_prefix,
    sys.base_exec_prefix,
}

if hasattr(sys, "real_prefix"):
    prefixes.add(sys.real_prefix)  # type: ignore[attr-defined,union-attr]

prefixes = tuple(prefixes)


def _has_level_handler(logger: logging.Logger) -> bool:
    """Check if there is a handler in the logging chain that will handle
    the given logger's effective level.

    :param logger: Logger object.
    :return: Handler level state.
    """
    level = logger.getEffectiveLevel()
    current = logger
    while current:
        if any(handler.level <= level for handler in current.handlers):
            return True
        if not current.propagate:
            break
        current = current.parent  # type: ignore[assignment]
    return False


def _log(level: str, msg: str, *args: Any, **kwargs: Any) -> None:
    """Log messages to the `xautic` logger.

    The logger is created the first time it is needed. If there is no
    level set, it is set to :py:data:`logging.INFO`. If there is no
    handler added for the logger's effective level,
    :py:class:`~logging.StreamHandler` is added.

    :param level: Logging level severity.
    :param msg: Message to be logged.

    .. warning::
        This is not a public API anymore, do not use this function.
    """
    global _logger
    if _logger is None:
        _logger = logging.getLogger("xautic.main")
        if _logger.level == logging.NOTSET:
            _logger.setLevel(logging.INFO)
        if not _has_level_handler(_logger):
            _logger.addHandler(logging.StreamHandler())
    getattr(_logger, level)(msg.rstrip(), *args, **kwargs)


def _imported_module_paths() -> Iterator[PathLike]:
    """Yield absolute paths of the imported modules.

    Loop over all the imported modules and try to get their absolute
    file paths. If the path consists of all directories and no file,
    then the implementation will break the loop and move on.
    """
    for module in list(sys.modules.values()):
        path = getattr(module, "__file__", None)
        if path is None:
            continue
        # We check if the module is running from a file or a directory.
        # If the path is a directory, we skip traversing the loop.
        while not os.path.isfile(path):
            tmp = path
            path = os.path.dirname(path)
            if path == tmp:
                break
        else:
            yield path


def _all_possible_paths(
    track: Set[PathLike], ignore_patterns: Set[str]
) -> Set[PathLike]:
    """Return list of paths for the reloader to track.

    Paths can be both for python and non-python files. While tracking
    python files, it also tracks the absolute paths of the imported
    modules. Here, we purposely exclude the system paths for efficiency.

    :param track: Absolute paths of both python & non-python files to
        track. Well, you can add non-python files to track but doing
        so might increase the CPU utilization. It is more advisable to
        track only python files e.g.: .py or .pyc.
    :param ignore_patterns: Path patterns to ignore. The patterns can be
        regular expressions or just names of the file(s) and directories
        to be ignored.
    :return: Set of all paths to track including the imported module
        paths and non-system file paths (python and non-python files).
    """
    paths = set()
    for path in itertools.chain(list(sys.path), track):
        path = os.path.abspath(path)
        if os.path.isfile(path):
            paths.add(path)
        for root, dirs, files in os.walk(path):
            if (
                root.startswith(prefixes)
                or os.path.basename(root) in IGNORED_DIRS
            ):
                dirs.clear()
                continue
            for file in files:
                if file.endswith(VALID_PY_FILES):
                    paths.add(os.path.join(root, file))
    paths.update(_imported_module_paths())
    for pattern in ignore_patterns:
        paths.difference_update(fnmatch.filter(paths, pattern))
    return paths


def _get_args_for_reloading() -> List[str]:
    """Return executable args."""
    execs = [sys.executable]
    py_script, *args = sys.argv
    # Here we're trying to understand how the script was called. There
    # are a lot of moving parts involved in this process. Simply running
    # `python3 test.py` might not be the case all the time.
    __main__ = sys.modules["__main__"]
    if getattr(__main__, "__package__", None) is None or (
        os.name == "nt"
        and __main__.__package__ == ""
        and not os.path.exists(py_script)
        and os.path.exists(f"{py_script}.exe")
    ):
        py_script = os.path.abspath(py_script)
        if os.name == "nt":
            if not os.path.exists(py_script) and os.path.exists(
                f"{py_script}.exe"
            ):
                py_script += ".exe"
            if (
                os.path.splitext(sys.executable)[1] == ".exe"
                and os.path.splitext(py_script)[1] == ".exe"
            ):
                execs.pop(0)
        execs.append(py_script)
    else:
        if sys.argv[0] == "-m":
            args = sys.argv
        else:
            if os.path.isfile(py_script):
                py_module = cast(str, __main__.__package__)
                name = os.path.splitext(os.path.basename(py_script))[0]
                if name != "__main__":
                    py_module += f".{name}"
            else:
                py_module = py_script
            execs.extend(("-m", py_module.lstrip(".")))
    execs.extend(args)
    return execs
