#!/usr/bin/env python3
"""Make sure the Python packages the hr-hiring skills need are installed.

Runs automatically when Claude starts (plugin SessionStart hook), and can be
run by hand. Fast when everything is already there.

1. If python-docx and pypdf import, nothing happens.
2. Otherwise it tries `pip install --user`.
3. If this Python refuses user installs (externally-managed), it creates a
   private environment at ~/JD-Builder/.venv and installs there.

Either way it writes the Python the skills should use to ~/JD-Builder/python,
which both skills read before running their scripts.

    python3 ensure_deps.py [--quiet] [--check]
"""
import subprocess
import sys
from pathlib import Path

PACKAGES = {"docx": "python-docx>=1.1", "pypdf": "pypdf>=4.0"}
HOME = Path.home() / "JD-Builder"
VENV = HOME / ".venv"
POINTER = HOME / "python"


def missing(python):
    code = "import importlib.util as u, sys; print(','.join(m for m in sys.argv[1:] if u.find_spec(m) is None))"
    r = subprocess.run([python, "-c", code, *PACKAGES], capture_output=True, text=True)
    if r.returncode != 0:
        return list(PACKAGES)
    return [m for m in r.stdout.strip().split(",") if m]


def pip(python, args):
    return subprocess.run([python, "-m", "pip", "install", "--disable-pip-version-check", "-q", *args],
                          capture_output=True, text=True)


def say(msg, quiet):
    if not quiet:
        print(msg)


def main():
    quiet = "--quiet" in sys.argv
    HOME.mkdir(parents=True, exist_ok=True)
    if sys.version_info < (3, 9):
        print(f"hr-hiring: Python {sys.version.split()[0]} is too old; install Python 3.9 or newer.")
        return 1
    venv_py = VENV / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")

    # Already set up in the private environment?
    if venv_py.exists() and not missing(str(venv_py)):
        POINTER.write_text(str(venv_py))
        say("hr-hiring: Python packages ready (private environment).", quiet)
        return 0
    need = missing(sys.executable)
    if not need:
        POINTER.write_text(sys.executable)
        say("hr-hiring: Python packages ready.", quiet)
        return 0
    if "--check" in sys.argv:
        print(f"hr-hiring: missing {', '.join(PACKAGES[m] for m in need)}")
        return 1

    reqs = [PACKAGES[m] for m in need]
    r = pip(sys.executable, ["--user", *reqs])
    if r.returncode == 0 and not missing(sys.executable):
        POINTER.write_text(sys.executable)
        print(f"hr-hiring: installed {', '.join(reqs)}.")
        return 0

    # Fall back to a private virtual environment.
    if not venv_py.exists():
        v = subprocess.run([sys.executable, "-m", "venv", str(VENV)], capture_output=True, text=True)
        if v.returncode != 0:
            print("hr-hiring: could not install Python packages. Ask IT to install "
                  f"{', '.join(PACKAGES.values())} for {sys.executable}.\n{(r.stderr or v.stderr).strip()[-400:]}")
            return 1
    r2 = pip(str(venv_py), list(PACKAGES.values()))
    if r2.returncode == 0 and not missing(str(venv_py)):
        POINTER.write_text(str(venv_py))
        print(f"hr-hiring: installed {', '.join(PACKAGES.values())} in {VENV}.")
        return 0
    print(f"hr-hiring: could not install Python packages.\n{r2.stderr.strip()[-400:]}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
