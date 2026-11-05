# Agentic AI for Everything (AI Expo Thailand 2026 talk site)

- Live: https://agentic-ai-for-everything.vercel.app (Vercel gen-ai-space, linked from cover/)
- Deploy: cd cover && vercel deploy --prod --yes --scope gen-ai-space
- Built from ai-for-work-weblink cover/ (WEBLINK_STANDARD). Work lessons are local copies; Creative pages embed ai-for-creative-work.vercel.app/menu.html?embed=1#lesson/N; Vibe pages embed vibe-code-weblink.vercel.app/decks/deck-NN.html?embed=1#N
- Cover: three.js globe (assets/earth textures from three.js examples) + Gen AI Space word.
- Contents + lesson viewer background: cover/assets/space-bg.js (earth turning in place, orbiting stars; falls back to the CSS sky without WebGL).
- Embedded-page thumbnails (strip + slide picker for `profile-site` pages): cover/assets/page-thumbs/<slug>.jpg. Re-run `python scripts/make-page-thumbs.py` after changing embedded pages (needs `pip install playwright pillow` + Chrome; `--missing` does only new pages). Missing image falls back to the text tile.
- TODO: meeting-recap-pro step-by-step pages (real Claude Desktop run); VaroCoin claim slide (Boss writes).

- The talk copy of cover/vibe/deck-04.html is trimmed to 9 steps; re-running scripts/apply-space-skin.py would undo this on refetch without its trim_talk_deck function, which reapplies the trim.

- How-to clips (Setup menu + AI Work Playbook): REAL screen recordings of Claude Desktop on the trainer's PC, cut only (speed-up, captions, privacy blur). Pipeline in scripts/howto/: make_jobs.py (prompts verbatim from the pages + fresh workspace per job) -> record-job.ps1 (drives Claude Desktop, records with ffmpeg gdigrab) -> make_spec.py + edit.py (cut to cover/assets/videos/howto-<id>.mp4). record-open.ps1 + fix_open.py redo only the 'open the output file' ending. Inputs for the Setup cards: cover/assets/playbook-samples/setup-*.

- Talk copy of cover/creative/menu.html is hand-edited: Varoriya page 1 no longer says "ดูในหน้า 4–6" (2026-11-05). Re-running scripts/apply-space-skin.py refetches it and undoes this; re-apply by hand.
- Talk copy: Varoriya pages 7 and 9 rewritten as one page each (Claude / ChatGPT MCP connect), 2026-11-05.
- Talk copy: Varoriya page 1 lost its "ตัวอย่างงานจริง" strip; new section 18 "ผลงานจริง 6 คลิป" appended after section 17 (2026-11-05).
- Talk copy: Varoriya page 16 rewritten as web prompts (Seedream Pro, Seedance 2.5, Grok Pro, OmniHuman lip sync, Seed Audio), no MCP wording (2026-11-05).
- IMPORTANT (2026-11-05): run `python scripts/strip-unused.py` after apply-space-skin.py or any menu page-list change. It blanks every embedded slide the talk does not show (no full course hand-out) and adds a guard so copies only open inside the viewer.
- Talk Vibe Code Way: 6-skill zip at cover/assets/skills/vibe-code-way-6-skills.zip (scrutinize + debug-mantra removed); deck-04 text fixes live in TALK_TEXT_FIXES in apply-space-skin.py; git prompt page = deck-02 #8 (2026-11-05).
