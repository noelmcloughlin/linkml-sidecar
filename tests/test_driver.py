"""The scaffold's driver: which interpreter runs the Python half.

The order is knowledge-trust-ladder's: `uv run` on the half's own header
first, then python3, then python as the last resort, each of the last two
only when it is 3.8 or later. Stand-ins on PATH record how they were
called, so no Python half runs here, and PATH holds nothing else the
driver could find on this machine.
"""

from __future__ import annotations

import re
import shutil

from conftest import SCAFFOLD, SCAFFOLD_PY, run

HALF = str(SCAFFOLD_PY.resolve())


def drive(tmp_path, **tools):
    """Run the driver with only the named stand-ins on PATH; True means a Python of 3.8 or later."""
    bindir = tmp_path / "bin"
    bindir.mkdir()
    (bindir / "dirname").symlink_to(shutil.which("dirname"))
    for name, recent in tools.items():
        stub = bindir / name
        stub.write_text(f'#!/bin/sh\nif [ "$1" = -c ]; then exit {0 if recent else 1}; fi\necho "{name} ran: $*"\n', encoding="utf-8")
        stub.chmod(0o755)
    return run([shutil.which("bash"), SCAFFOLD, "--dry-run"], env={"PATH": str(bindir)})


def test_uv_runs_the_python_half_first(tmp_path):
    done = drive(tmp_path, uv=True, python3=True, python=True)
    assert done.rc == 0 and done.out == f"uv ran: run --quiet {HALF} --dry-run"


def test_without_uv_a_python3_of_3_8_or_later_runs_it(tmp_path):
    done = drive(tmp_path, python3=True, python=True)
    assert done.rc == 0 and done.out == f"python3 ran: {HALF} --dry-run"


def test_python_is_the_last_resort(tmp_path):
    done = drive(tmp_path, python3=False, python=True)
    assert done.rc == 0 and done.out == f"python ran: {HALF} --dry-run"


def test_an_older_python_and_no_uv_stop_with_exit_2(tmp_path):
    done = drive(tmp_path, python3=False, python=False)
    assert done.rc == 2 and "needs uv, or python3 3.8 or later" in done.out


def test_the_half_s_header_names_no_package_for_a_mirror_to_refuse():
    header = re.search(r"^# /// script\n(.*?)^# ///$", SCAFFOLD_PY.read_text(encoding="utf-8"), re.M | re.S).group(1)
    assert '# requires-python = ">=3.8"' in header
    assert "# dependencies = []" in header and "exclude-newer" not in header
