# Default imports
import subprocess

# Local imports
from .exceptions import BFSExecutorError


def run_process(
    cmd,
    is_shell_cmd=None,
    print_output=None,
    output_stream=None,
    error_stream=None,
    raise_exception=None,
    convert_response_text=None,
):
    """
    Runs the given cmd Sequence in the process and wait to complete.

    Args:
        cmd (list): Command sequence to run in the process.
        is_shell_cmd (bool, optional): If True, the command will be executed through the shell.
            Defaults to False.
        print_output (bool, optional): If True, the output will be printed to the console.
            Defaults to False.
        output_stream (file-like object, optional): Stream to which standard output will be directed.
            Defaults to None.
        error_stream (file-like object, optional): Stream to which standard error will be directed.
            Defaults to None.
        raise_exception (bool, optional): If True, exceptions will be raised for non-zero

    Return: subprocess.CompletedProcess Object.

    """
    if not isinstance(cmd, list):
        msg = (
            f"args value for 'cmd' parameter must be a 'list' type but got {cmd.type()}"
        )
        raise BFSExecutorError(
            msg,
        )

    args = {
        "args": cmd,
        "shell": is_shell_cmd or False,
        "check": raise_exception or True,
        "text": convert_response_text or True,
        "universal_newlines": True,
    }
    if print_output:
        if output_stream:
            args["stdout"] = output_stream
        if error_stream:
            args["stderr"] = error_stream
    else:
        args["capture_output"] = True

    try:
        called_process_instance = subprocess.run(**args)  # noqa: PLW1510

    except FileNotFoundError as exc:
        raise BFSExecutorError(
            (
                "'Program' or 'Script' not found in target system.",
                "Please validate cmd sequence provided.",
                f"For more details refer the execution output {exc}",
            ),
        ) from exc
    except subprocess.TimeoutExpired as exc:
        raise BFSExecutorError(
            (
                "Process cmd Took long time complete.",
                f"For more details refer the execution output {exc}",
            ),
        ) from exc

    except subprocess.CalledProcessError as exc:
        raise BFSExecutorError(
            (
                "Process cmd return non zero return code.",
                f"For more details refer the execution output {exc}",
            ),
        ) from exc
    return called_process_instance
