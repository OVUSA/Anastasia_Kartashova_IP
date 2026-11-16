# Excel Growth — landing page

Static one-page site (Russian) for corporate Excel training and business analytics.
No dependencies: only Python 3.8+ is needed to build it.

## Project layout

| Path | What it is |
|---|---|
| `content.json` | **All text and contacts.** Edit this for content changes. |
| `style.css` | Appearance. |
| `form.js` | Contact-form behaviour. |
| `build.py` | Page structure; generates `dist/`. |
| `assets/` | Images (logo, mark, favicon). |
| `originals/` | Untouched source images (not published). |
| `dist/` | **Generated** by `build.py`, git-ignored. Never edit by hand: it is wiped on every build. |

## Build and preview locally

```bash
python build.py
cd dist && python -m http.server 8000   # open http://localhost:8000
```
## Making changes

Edit `content.json` / `style.css` / `form.js` / `build.py`, run `python build.py` to check locally,
then commit and push; the site republishes automatically.
