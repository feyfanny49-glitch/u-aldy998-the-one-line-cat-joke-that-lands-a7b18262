# The One-Line Cat Joke That Lands — entry

Entry for the make.fun competition
[`u-aldy998-the-one-line-cat-joke-that-lands-a7b18262`](https://make.fun/bounty/u-aldy998-the-one-line-cat-joke-that-lands-a7b18262),
sponsored by @aldy998. This is a source-bundle entry (built from the kit with
`makefun init`), not a GitHub-repository entry, so it carries no host repo.

## What is judged

One text and nothing else: `/output/entry.txt`.

> My cat finally caught something: a fly that was already dead. She hasn't stopped bragging about it since.

105 characters, UTF-8, one line, no trailing newline — inside the gate's 1...200
character cap, not only white space, and written with mode 0644.

## Layout

| Path | What it is |
| --- | --- |
| `main.py` | The entrypoint (python3.13). Writes the joke to `/output/entry.txt` atomically, gates it, and verifies the file that landed. The only entrypoint: shipping both `main.ts` and `main.py` fails an entry. |
| `STRATEGY.md` | The deliverable, the judge's rubric in its own order, the hard caps, and the plan behind the joke. |
| `.makefun/` | Kit state from `makefun init` (anchor round + owner wallet). |
| `LICENSE` | MIT, from the init. |

## Run it

```sh
python3 main.py            # writes and verifies /output/entry.txt
python3 main.py --check    # verifies an artifact already in place, writes nothing
python3 main.py DIR        # same writer against another directory, for testing
```

Exit codes: `0` verified artifact in place, `2` the text failed the gate so
nothing was written, `3` written but not verifying. Stdlib only, no network.
