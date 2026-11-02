# Agentic AI for Everything (AI Expo Thailand 2026 talk site)

- Live: https://agentic-ai-for-everything.vercel.app (Vercel gen-ai-space, linked from cover/)
- Deploy: cd cover && vercel deploy --prod --yes --scope gen-ai-space
- Built from ai-for-work-weblink cover/ (WEBLINK_STANDARD). Work lessons are local copies; Creative pages embed ai-for-creative-work.vercel.app/menu.html?embed=1#lesson/N; Vibe pages embed vibe-code-weblink.vercel.app/decks/deck-NN.html?embed=1#N
- Cover: three.js globe (assets/earth textures from three.js examples) + Gen AI Space word.
- Contents + lesson viewer background: cover/assets/space-bg.js (earth turning in place, orbiting stars; falls back to the CSS sky without WebGL).
- Embedded-page thumbnails (strip + slide picker for `profile-site` pages): cover/assets/page-thumbs/<slug>.jpg. Re-run `python scripts/make-page-thumbs.py` after changing embedded pages (needs `pip install playwright pillow` + Chrome; `--missing` does only new pages). Missing image falls back to the text tile.
- TODO: meeting-recap-pro step-by-step pages (real Claude Desktop run); VaroCoin claim slide (Boss writes).

- The talk copy of cover/vibe/deck-04.html is trimmed to 9 steps; re-running scripts/apply-space-skin.py would undo this on refetch without its trim_talk_deck function, which reapplies the trim.
