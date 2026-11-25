---
name: commit-and-push
description: Commit and push every change made in this save folder (game scripts, old/, the tfwr-sim skill, config). Use after any edit to a file in this repo, before ending the turn.
---

# Commit and push changes in this save folder

This save folder is the git repo `github.com/u9g/the-farmer-was-replaced` (branch `main`). Every
change made here gets committed and pushed straight to `main` in the same turn, without asking
first. No branch and no PR.

## Steps

1. `git status --short` to see what changed.
2. Stage the files you changed by name (`git add cactus.py .claude/skills/tfwr-sim/tfwr_sim.rs`),
   not `git add -A`. Leave alone any change you did not make, such as a script the player is
   editing in the game, unless the user asked to commit it.
3. Commit with a short message that says what changed and why, e.g.
   `cactus: mesh sort with 100 sort slots (3.9M -> 4.2M/min at 16x16)`.
   No Claude attribution: no `Co-Authored-By` trailer, no "Generated with" line.
4. `git push`. If it is rejected, `git pull --rebase` and push again.
5. Tell the user the commit link: `https://github.com/u9g/the-farmer-was-replaced/commit/<sha>`.

## save.json

Never commit or push `save.json`; the user does not want it published. It is in `.gitignore`.
Do not `git add -f` it, and do not run `git add`, `git diff` or `git show` on it: the game
rewrites it every 30 seconds with `File.Replace`, and if anything holds the file open at that
moment the game's whole save fails, code included.

## Other files

- Scratch variants of scripts belong in the scratchpad, not here: the game deletes `.py` files it
  does not know from the save folder, and they would end up committed.
- `save.json`, `.ruff_cache/`, `__pycache__/` and the game's temporary save files are in
  `.gitignore`.
