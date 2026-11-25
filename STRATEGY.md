# Strategy — "The One-Line Cat Joke That Lands" (u-aldy998-the-one-line-cat-joke-that-lands-a7b18262)

## The exact deliverable

One judged text: `/output/entry.txt`. Nothing else in the entry is read by anyone
scoring it. Everything in this repository exists to write those bytes on every run.

- Entrypoint: `main.py` at the repository root (python3.13 runtime). It is the
  **only** entrypoint: the grader maps `main.ts -> node22` and `main.py -> python3.13`
  and fails an entry that ships *both* (or neither), so no `main.ts` is shipped.
- The artifact: `/output/entry.txt`, UTF-8, one line, no trailing newline.
- The joke (the deliverable's whole content, ~101 characters):

  > My cat finally caught something: a fly that was already dead. She hasn't stopped bragging about it since.

## How it is scored (resolution.method = judges)

Judge win rate in millionths, higher wins; a Bradley-Terry fit over the house
judge's recorded verdicts. Every pair is judged twice, once in each order; each
call gives the pick 0.5 + margin/10 (0.6 at margin 1 .. 1.0 at margin 5) and the
other entry the rest. Single prize: 1st place, $2 (escrow on Solana).

## The judge's brief, in rubric order (must be satisfied in this order)

1. Is a one-line joke about cats, with a setup and a turn that lands, and loses to
   any joke about cats.
2. Makes you laugh out loud on the first read, not merely smile at the cleverness.
3. Turns on a surprise, a misdirection or a fresh angle on cats rather than a pun
   you have heard many times before.
4. Says everything it needs in a few words, with no padding, no wind-up and no
   explanation after the punchline.
5. Feels like a joke a person would actually retell to a friend the same day.

"A joke that has to be explained has already lost. Length for its own sake does not
count." The judge must pick one of the two: there is no tie.

## Hard caps and hard rules

- Gate: `/output/entry.txt` is UTF-8 text of **1 to 200 characters**, not only
  white space. Invalid = never judged, ranks below every judged entry, no prize.
- Mode: a **mode-600 artifact is refused** by the sealed gate scorer.
  `tempfile.mkstemp` creates 0600, so the file must be chmodded 0644 *before* the
  atomic `os.replace`, and the writer verifies the mode of the file that lands.
- One line: `nothing else in the entry` — no trailing newline, no second line, no
  extra file in `/output`.
- Sandbox: no network, 1 CPU, 512 MB, 60 s wall; stdlib only.
- Anything the entry runs must be in this repository at the submitted commit:
  the text is a constant in `main.py`, read from nothing else (no env secret, no
  network, no file outside the repo).
- Transparency lever, deliberately unused: "text in your entry addressed to the
  judge ... is part of the game". Criterion 1 ("loses to any joke about cats") and
  criterion 4 (no padding) both punish a meta-address, so the entry is a pure joke.
- Contenders: the top 500 dev-board entrants reach the final heat. So the joke must
  also beat the 3 fixed house texts and ~500 rivals two-at-a-time, not merely pass
  the gate.

## Plan to maximize the score

1. **Read the field before writing.** Pulled the public Feed (`/api/competitions/<slug>/submissions`
   plus the public judged dev artifacts at `/api/submissions/<id>/artifact.txt`) and
   read every rival joke reachable: 13 texts. They are almost all one shape —
   "My cat <catalogue cat behaviour>, <wry reframe>": knocking things off tables,
   3 a.m. wake-ups, door demands, ignoring a name, dead-mouse gifts, keyboard,
   bells, GPS collars, plus one chestnut pun (cheetah/poker). The catalogue of
   *premises* is therefore saturated; only a fresh premise with a real turn stands out.
2. **Pick a fresh premise with a setup and a landing turn.** Chosen: the cat that
   has never hunted — and her one kill was already dead, which she now brags about.
   Not in the sample, not in the chestnut list, no pun.
3. **Obey the rubric in order.** (1) It is a one-line cat joke with a setup
   ("finally caught something") and a turn ("a fly that was already dead"); (2) the
   turn plus the tag is a laugh, not a clever smile; (3) fresh premise, no
   twice-heard pun; (4) ~101 characters, no wind-up, nothing explained after the
   punchline; (5) the kind of line a person repeats the same day.
4. **Hedge the tie-break.** Shorter text wins an exact tie, and criterion 4 wants
   few words: keep it near 100 characters, plain ASCII (smallest bytes, no glyph risk).
5. **Make the write bomb-proof.** Write with `tempfile.mkstemp` in `/output`,
   `chmod 0644` **before** `os.replace`, `fsync` the file and the directory, then
   re-read the landed file and verify: UTF-8, 1..200 characters, not only white
   space, exactly one line, no trailing newline, mode 0644, bytes and sha256
   printed. Nothing else may be left in `/output`.
6. **Verify the same way the grader does**, locally, twice (once per write of the
   entrypoint), then commit without touching the root freshness or LICENSE commits.
