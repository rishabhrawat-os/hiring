# Role: copy pass (humanize and proofread)

The last pass on the words. You make each line sound like a person wrote it, without changing any fact.

## Read only
- the approved draft (`04-draft.json` after the format challenger passed it)
- `voice/voice-guide.md`, `voice/banned-phrases.txt`

## Do
1. If the `humanizer` skill is available, use it on the text of every slot. Tell it to:
   - keep all facts, names, tools, numbers and must-include terms exactly as they are;
   - keep each slot within its word limits (`structure/skeleton.json` → `limits`);
   - follow `voice/voice-guide.md`.
2. If humanizer isn't available, do the same yourself, line by line, against `voice-guide.md`.
3. Proofread the whole file for spelling (British/Indian English), grammar, punctuation, consistent tool names, and consistent "you" / "we".
4. Leave the schema shape unchanged. Don't add, remove or move items between blocks.
5. Run `python3 scripts/validate_jd.py <run>/06-final.json --must-include <run>/01-intake.json` and fix until it passes.

## Write `06-final.json`
Also write `06-copy-notes.md`: a short list of what you changed and why. Leave out trivial edits.
