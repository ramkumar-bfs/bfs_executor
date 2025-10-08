"""
Subprocess execution utilities for BFS executor.

Provides a single entry point `run_process` to run commands safely with
clear error handling suitable for production use.
"""

from __future__ import annotations

# Default imports
import subprocess
from typing import IO

# Local imports
from .exceptions import BFSExecutorError


def run_process(
    cmd: list[str],
    *,
    is_shell_cmd: bool = False,
    print_output: bool = False,
    output_stream: IO[str] | None = None,
    error_stream: IO[str] | None = None,
    raise_exception: bool = True,
    convert_response_text: bool = True,
) -> subprocess.CompletedProcess:
    """
    Run the given command sequence in a subprocess and wait for completion.

    Args:
        cmd: Command sequence to run in the process (list of strings).
        is_shell_cmd: If True, run the command through the shell. Defaults to False.
        print_output: If True, stream output to provided streams/console. Defaults to False.
        output_stream: Stream for standard output when print_output is True.
        error_stream: Stream for standard error when print_output is True.
        raise_exception: If True, raise for non-zero exit codes. Defaults to True.
        convert_response_text: If True, return output as text. Defaults to True.

    Returns:
        subprocess.CompletedProcess: The completed process instance.

    Raises:
        BFSExecutorError: If input is invalid or the process fails.

    """
    # Validate input
    if not isinstance(cmd, list) or not all(isinstance(x, str) for x in cmd):
        msg = (
            f"'cmd' must be a list of strings, got type={type(cmd).__name__} "
            f"value={cmd!r}"
        )
        raise BFSExecutorError(msg)

    # Compute effective flags
    shell = is_shell_cmd
    check = raise_exception
    text = convert_response_text
    stream_output = print_output

    run_kwargs: dict = {
        "args": cmd,
        "shell": shell,
        # "check": check, # This is set below to allow capture_output logic
        "text": text,
        "universal_newlines": text,
    }

    if stream_output:
        if output_stream is not None:
            run_kwargs["stdout"] = output_stream
        if error_stream is not None:
            run_kwargs["stderr"] = error_stream
    else:
        # Capture output when not streaming to simplify error reporting
        run_kwargs["capture_output"] = True

    try:
        result = subprocess.run(check=check, **run_kwargs)
    except FileNotFoundError as exc:
        msg = (
            f"Program or script not found: {cmd[0]!r}. "
            f"Validate the command sequence. Details: {exc}"
        )
        raise BFSExecutorError(msg) from exc
    except subprocess.TimeoutExpired as exc:  # pragma: no cover (only if timeout used)
        msg = f"Process command timed out. Details: {exc}"
        raise BFSExecutorError(msg) from exc
    except subprocess.CalledProcessError as exc:
        # Include return code and any captured output to aid debugging
        stdout = getattr(exc, "stdout", None)
        stderr = getattr(exc, "stderr", None)
        details = []
        details.append(f"exit_code={exc.returncode}")
        if stdout:
            details.append(f"stdout={stdout!r}")
        if stderr:
            details.append(f"stderr={stderr!r}")
        msg = "Process command returned non-zero exit code: " + ", ".join(details)
        raise BFSExecutorError(msg) from exc
    except Exception as exc:  # Defensive catch-all with context
        msg = f"Unexpected error running process: {exc}"
        raise BFSExecutorError(msg) from exc

    return result
