# Article Publisher - Project Instructions

## Medium Publishing Rules (MANDATORY)

These rules were learned the hard way across multiple failed sessions. Follow them exactly.

### HTML Tables → Images
- **Medium does NOT support HTML `<table>` tags.** They render as broken plain text.
- ALL tables must be converted to PNG images before import.
- Use `lib/table_image_generator.py` (PIL/Pillow) to generate table images.
- Format: `<p><img src="..." alt="..." /></p>` — always wrap in `<p>` tags.

### Image URLs
- **NEVER use `raw.githubusercontent.com` URLs.** Medium rejects them (serves `text/plain`).
- **ALWAYS use GitHub Pages URLs**: `https://ghighcove.github.io/article-publisher/articles/<slug>/<image>.png`
- Verify images are accessible with curl before telling the user they're ready.

### HTML Manipulation
- **NEVER use `sed` for HTML replacement on Windows.** It corrupts tags (e.g., creates `</p></p>` double-closing).
- **ALWAYS use Python** with `re.sub()` for HTML table-to-image replacement.
- After ANY HTML modification, read the output file and verify:
  - Zero `<table>` tags remain
  - Zero `</p></p>` corruptions
  - Correct count of `<img>` tags
  - All URLs use `ghighcove.github.io`

### Cache Bypass
- If Medium keeps importing an old/broken version, use a **new filename** (e.g., `medium.html` instead of `index.html`). Medium caches imports by URL.

### Deployment Verification
- After pushing to GitHub, wait 30-35 seconds for GitHub Pages deployment.
- `curl` the deployed URL and verify the HTML content matches expectations.
- **Never tell the user "it's ready" until the deployed version is verified.**

## Rebuild Over Patch
- When HTML is corrupted, **rebuild from the original source**, don't try to patch the broken file.
- Source HTML lives in the project's temp directory (see `tasks/context.md` for paths).
- A clean rebuild takes 30 seconds. Debugging cascading patches wastes entire sessions.

## Verification Protocol
- After any file modification: **read the file and show proof**.
- When user reports something broken: **check immediately, don't hypothesize first**.
- Never say "it's fixed" — say "I've verified: [evidence]".
