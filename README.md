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

## Before publishing: fill in `content.json`

| Key | Value |
|---|---|
| `site_url` | The real public address, e.g. `https://username.github.io/repo-name` or your own domain. Used for canonical link, sitemap, `robots.txt`, social preview. |
| `form.endpoint` + `form.access_key` | Contact-form delivery (see below). |
| `contacts`, `legal_extra` | Already filled in; check they are correct. |
| `yandex_verification`, `metrika_id` | Optional: add as top-level keys for Yandex Webmaster / Metrika. |

### Contact form

The page has no server, so the form posts to a third-party service that emails the submissions.
Set **one** of these in `content.json` → `form`:

1. **Web3Forms** (simplest): get a free access key for your email at <https://web3forms.com>, then
   `"endpoint": "https://api.web3forms.com/submit"` and `"access_key": "<your key>"`.
2. **Formspree**: create a form at <https://formspree.io>, then
   `"endpoint": "https://formspree.io/f/<id>"` (leave `access_key` empty).
3. **Yandex Forms**: build a form at <https://forms.yandex.ru>, copy its embed link into
   `"yandex_forms_url"`. This replaces the built-in form (and ignores `endpoint`).

These keys/endpoints are designed to be public, so it is safe to commit them.
If none is set, the form shows an error on submit, and `build.py` prints a warning.

## Deploy to GitHub Pages

1. Create a repository on GitHub and push this folder to the `main` branch.
2. In the repository: **Settings → Pages → Build and deployment → Source: GitHub Actions**.
3. Every push to `main` runs `.github/workflows/deploy.yml`, which runs `python build.py` and publishes `dist/`.
   The address appears in the workflow run (and under Settings → Pages).
4. Set `site_url` in `content.json` to that address and push again.

A custom domain can be added under Settings → Pages. Update `site_url` to match.

## Making changes

Edit `content.json` / `style.css` / `form.js` / `build.py`, run `python build.py` to check locally,
then commit and push; the site republishes automatically.
