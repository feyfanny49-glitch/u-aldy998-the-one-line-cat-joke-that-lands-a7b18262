#!/usr/bin/env python3
"""Entry for make.fun "The One-Line Cat Joke That Lands".

The judge reads exactly one text — /output/entry.txt — and nothing else in this
repository is scored. The whole deliverable is therefore the JOKE below, and this
program's only job is to put those exact bytes in /output/entry.txt in the one
shape the gate accepts.

Gate (kit competition.yaml + RULES.txt): /output/entry.txt is UTF-8 text of 1 to
200 characters, not only white space; it is the entry's only line, and the sealed
gate scorer refuses an artifact whose mode is 0600. An entry that fails the gate
is never judged, ranks below every judged entry and takes no prize.

So the writer does all of this, in this order:
  1. gate the text in memory (encodable, 1..200 characters, not only white space,
     a single line, no trailing newline) and refuse to write anything if it fails;
  2. write it with tempfile.mkstemp, chmod 0644 BEFORE the atomic os.replace
     (mkstemp creates 0600, which the gate would refuse), fsync file and directory;
  3. sweep only its own abandoned temp files, and warn about any other file it
     did not put in /output;
  4. re-read the file that actually landed and verify bytes, sha256, mode 0644 and
     the gate again, so a silent failure cannot end a run looking like a success.

Exit codes: 0 the verified artifact is in place; 2 the text failed the gate and
nothing was written; 3 /output was written but does not verify.

Usage: main.py [OUTPUT_DIR]   (default /output; the argument exists only to
exercise the writer outside the sandbox)   main.py --check [OUTPUT_DIR]  verifies
an artifact already on disk without writing.
"""

from __future__ import annotations

import hashlib
import os
import sys
import tempfile

# The entry: one line, no trailing newline, 105 characters, plain ASCII. Plain
# over-the-wire bold and euro glyph dodging are irrelevant here — this is text —
# but ASCII keeps bytes and characters equal, so no length reading can disagree.
JOKE = (
    "My cat finally caught something: a fly that was already dead. "
    "She hasn't stopped bragging about it since."
)

DEFAULT_OUTPUT_DIR = "/output"
ARTIFACT_NAME = "entry.txt"
TEMP_PREFIX = ".entry-"
MAX_CHARS = 200
ARTIFACT_MODE = 0o644
LINE_BREAKS = ("\n", "\r", "\u2028", "\u2029")


def gate_failures(text: str) -> list[str]:
    """Every reason the gate would reject this text, so the log names them all."""
    reasons: list[str] = []
    if not text:
        reasons.append("empty")
    if len(text) > MAX_CHARS:
        reasons.append(f"{len(text)} characters, past the {MAX_CHARS}-character cap")
    if not text.strip():
        reasons.append("only white space")
    for break_char in LINE_BREAKS:
        if break_char in text:
            where = text.index(break_char)
            reasons.append(f"line break {break_char!r} at offset {where}")
    try:
        text.encode("utf-8")
    except UnicodeEncodeError as error:
        reasons.append(f"not encodable as UTF-8: {error}")
    return reasons


def output_path(directory: str) -> str:
    return os.path.join(directory, ARTIFACT_NAME)


def write_artifact(path: str, payload: bytes) -> None:
    """Write payload to path atomically with mode 0644, then make it durable."""
    directory = os.path.dirname(path) or "."
    handle_fd, tmp = tempfile.mkstemp(dir=directory, prefix=TEMP_PREFIX, suffix=".tmp")
    try:
        with os.fdopen(handle_fd, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(tmp, ARTIFACT_MODE)  # before the replace: mkstemp made 0600
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except FileNotFoundError:
            pass
        raise
    directory_fd = os.open(directory, os.O_RDONLY)
    try:
        os.fsync(directory_fd)
    finally:
        os.close(directory_fd)


def sweep_own_temps(directory: str) -> list[str]:
    """Delete temp files an earlier run abandoned; touch nothing else."""
    swept: list[str] = []
    for name in sorted(os.listdir(directory)):
        if name.startswith(TEMP_PREFIX):
            try:
                os.unlink(os.path.join(directory, name))
                swept.append(name)
            except OSError:
                pass
    return swept


def verify(path: str, expected: bytes) -> tuple[list[str], os.stat_result | None]:
    """Read the artifact that landed and check it against the gate."""
    problems: list[str] = []
    if not os.path.isfile(path):
        return [f"{path} is not a regular file"], None
    stat = os.stat(path)
    with open(path, "rb") as handle:
        payload = handle.read()
    mode = stat.st_mode & 0o777
    if mode != ARTIFACT_MODE:
        problems.append(f"mode {mode:04o}, not {ARTIFACT_MODE:04o}")
    if payload != expected:
        problems.append("bytes on disk differ from the bytes written")
    try:
        text = payload.decode("utf-8")
    except UnicodeDecodeError as error:
        problems.append(f"not valid UTF-8: {error}")
    else:
        problems.extend(gate_failures(text))
    return problems, stat


def report(path: str, payload: bytes, stat: os.stat_result | None) -> None:
    text = payload.decode("utf-8", "replace")
    print(f"artifact {path}")
    if stat is not None:
        print(f"mode     {stat.st_mode & 0o777:04o}   bytes {stat.st_size}")
    print(f"chars    {len(text)}   lines {len(text.splitlines()) or 0}"
          f"   trailing newline {payload.endswith(b'\n')}")
    print(f"sha256   {hashlib.sha256(payload).hexdigest()}")
    print(f"entry    {text}")


def main(argv: list[str]) -> int:
    args = [arg for arg in argv[1:] if arg != "--check"]
    check_only = "--check" in argv[1:]
    directory = args[0] if args else DEFAULT_OUTPUT_DIR
    path = output_path(directory)
    payload = JOKE.encode("utf-8")

    failures = gate_failures(JOKE)
    if failures:
        print(f"gate     FAILED, nothing written: {'; '.join(failures)}", file=sys.stderr)
        return 2

    print(f"gate     ok: {len(JOKE)} characters (cap {MAX_CHARS}), "
          f"one line, not only white space, UTF-8")
    if check_only:
        print("mode     check only, nothing written")
    else:
        os.makedirs(directory, exist_ok=True)
        write_artifact(path, payload)
        swept = sweep_own_temps(directory)
        if swept:
            print(f"swept    {len(swept)} abandoned temp file(s): {' '.join(swept)}")
        foreign = [
            name
            for name in sorted(os.listdir(directory))
            if name != ARTIFACT_NAME and not name.startswith(TEMP_PREFIX)
        ]
        if foreign:
            print(f"warning  other files in {directory}: {' '.join(foreign)}")

    problems, stat = verify(path, payload)
    report(path, payload, stat)
    if problems:
        for problem in problems:
            print(f"problem  {problem}", file=sys.stderr)
        return 3
    print("verified ok: UTF-8, 1..200 characters, one line, mode 0644")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
