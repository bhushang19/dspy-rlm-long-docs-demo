"""Windows-compatible PythonInterpreter factory for DSPy RLM."""

from __future__ import annotations

import os

from dspy.primitives.python_interpreter import PythonInterpreter


def build_windows_interpreter() -> PythonInterpreter:
    """Return a PythonInterpreter configured to work on Windows.

    On Windows, Deno is often only available as a .cmd/.ps1 wrapper (e.g. installed
    via npm or Chocolatey). subprocess.Popen cannot invoke those wrappers directly.
    This function resolves a real deno.exe, grants it read access to its own module
    cache (which DSPy's _get_deno_dir() fails to detect on Windows), and disables
    TLS certificate validation so that deno.land imports work through corporate
    proxies with self-signed certificates.
    """
    _tmp = PythonInterpreter.__new__(PythonInterpreter)
    runner_js = _tmp._get_runner_path()
    deno_dir = _tmp._get_deno_dir()

    allowed_read = [runner_js]
    if deno_dir:
        allowed_read.append(deno_dir)
    localappdata_deno = os.path.expandvars(r"%LOCALAPPDATA%\deno")
    if os.path.isdir(localappdata_deno):
        allowed_read.append(localappdata_deno)
    userprofile_deno = os.path.expandvars(r"%USERPROFILE%\.deno")
    if os.path.isdir(userprofile_deno):
        allowed_read.append(userprofile_deno)

    candidates = [
        os.path.expandvars(r"%USERPROFILE%\.deno\bin\deno.exe"),
        r"C:\deno\deno.exe",
        os.path.expandvars(r"%APPDATA%\npm\node_modules\deno\deno.exe"),
    ]
    deno_exe = next((p for p in candidates if os.path.isfile(p)), "deno")

    deno_command = [
        deno_exe, "run",
        "--unsafely-ignore-certificate-errors",
        f"--allow-read={','.join(allowed_read)}",
        "--allow-env",
        "--allow-net",
        runner_js,
    ]
    return PythonInterpreter(deno_command=deno_command)
