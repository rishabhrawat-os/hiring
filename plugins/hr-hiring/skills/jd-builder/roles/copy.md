# Role: copy pass (humanize and proofread)

The last pass on the words. You make each line sound like a person wrote it, without changing any fact.

## Read only
- the approved draft (`run.json` → `approved_draft`)
- `$SKILL_DIR/voice/voice-guide.md`, `$SKILL_DIR/voice/banned-phrases.txt`, `$SKILL_DIR/structure/skeleton.json` (limits)

## Do
1. Use the humanizer skill on the text of every slot. It may be listed as `humanizer` or `anthropic-skills:humanizer`. Tell it to:
   - keep all facts, names, tools, numbers and must-include terms exactly as they are;
   - keep `**bold**` markup;
   - keep each slot within its word limits;
   - follow `voice-guide.md`.
2. If neither name is available, do the same yourself, line by line, against `voice-guide.md`. Either way, report `humanizer_used: true|false` to the orchestrator for `run.json`.
3. Proofread the whole file for spelling (British/Indian English), grammar, punctuation, consistent tool names, and consistent "you" / "we".
4. Leave the schema shape unchanged. Don't add, remove or move items between blocks.
5. Run `python3 "$SKILL_DIR/scripts/validate_jd.py" <run>/06-final.json --intake <run>/01-intake.json` and fix until it passes.

## Write `06-final.json`
Also write `06-copy-notes.md`: a short list of what you changed and why. Leave out trivial edits.
