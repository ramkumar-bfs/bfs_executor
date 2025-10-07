# Default imports
import subprocess

# Local imports
from .exceptions import BFSExecutorError


def run_process(
    cmd,
    is_shell_cmd=False,
    print_output=True,
    output_stream=None,
    error_stream=None,
    raise_exception=True,
    convert_response_text=True,
):
    """
    Runs the given cmd Sequence in the process and wait to complete.
    Return: subprocess.CompletedProcess Object
    """
    if not isinstance(cmd, list):
        raise BFSExecutorError(
            f"args value for 'cmd' parameter must be a 'list' type but got {cmd.type()}"
        )

    args = {
        "args": cmd,
        "shell": is_shell_cmd,
        "check": raise_exception,
        "text": convert_response_text,
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
        called_process_instance = subprocess.run(**args)

    except FileNotFoundError as exc:
        raise BFSExecutorError(
            (
                "'Program' or 'Script' not found in target system.",
                "Please validate cmd sequence provided.",
                f"For more details refer the execution output {exc}",
            )
        ) from exc
    except subprocess.TimeoutExpired as exc:
        raise BFSExecutorError(
            (
                "Process cmd Took long time complete.",
                f"For more details refer the execution output {exc}",
            )
        ) from exc

    except subprocess.CalledProcessError as exc:
        raise BFSExecutorError(
            ()(
                "Process cmd return non zero return code.",
                f"For more details refer the execution output {exc}",
            )
        ) from exc
    return called_process_instance
