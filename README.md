# Image Converter Tools

Free, static, client-side image converters for WebP, PNG and JPG. No backend, no
dependencies, no tracking. Images are decoded and re-encoded by the visitor's own
browser and never leave their device.

Live at **https://convert-img.me** — hosted free on GitHub Pages with a custom
domain, built for Google AdSense monetisation.

---

## Contents

- [Project layout](#project-layout)
- [Run it locally](#run-it-locally)
- [The build step](#the-build-step)
- [Adding a converter](#adding-a-converter)
- [Deploy to GitHub Pages](#deploy-to-github-pages)
- [Configure the site URL](#configure-the-site-url)
- [Add your Google AdSense code](#add-your-google-adsense-code)
- [Update the SEO metadata](#update-the-seo-metadata)
- [Search Console and Analytics](#search-console-and-analytics)
- [How the converters work](#how-the-converters-work)
- [Testing](#testing)
- [Limitations](#limitations)

---

## Project layout

```
.
├── index.html               Hub page listing every converter          ← generated
├── webp-to-png/index.html   ┐                                         ← generated
├── webp-to-jpg/index.html   │
├── png-to-jpg/index.html    ├ one directory per converter
├── jpg-to-png/index.html    │
├── png-to-webp/index.html   │
├── jpg-to-webp/index.html   ┘
├── privacy.html             Privacy policy                            ← generated
├── terms.html               Terms of use & disclaimer                 ← generated
├── contact.html             Contact details                           ← generated
├── 404.html                 Not-found page (absolute paths)           ← generated
├── sitemap.xml              All 10 indexable URLs                     ← generated
├── robots.txt                                                         ← generated
├── manifest.webmanifest     PWA manifest ("install" to home screen)   ← generated
├── .nojekyll                Tells GitHub Pages to serve files as-is
├── tools/
│   ├── content.py           ★ ALL page copy, FAQs and metadata live here
│   └── build.py             Wraps that content in the shared page shell
└── assets/
    ├── css/styles.css       The entire stylesheet
    ├── js/converter.js      Format registry, validation, decode, encode
    ├── js/app.js            UI: drop zone, file list, options, downloads
    ├── js/zip.js            Minimal "Download all as ZIP" writer
    ├── js/theme.js          Light/dark toggle
    └── img/                 favicon, PWA icons, per-tool social cards
```

Around 45 KB of HTML/CSS/JS per page, and zero third-party requests. Every page
carries the same four-item navigation (All tools · Privacy · Terms · Contact),
generated from one list in `build.py` so it cannot drift between pages.

## Run it locally

The JavaScript uses ES modules, which browsers refuse to load over `file://`.
Serve the folder over HTTP:

```bash
python3 -m http.server 8000     # then open http://localhost:8000
```

## The build step

The HTML files are **generated**, and the generated output is what GitHub Pages
serves. There is no build at deploy time — the build runs on your machine, and
you commit the result.

```bash
python3 tools/build.py          # requires only the Python standard library
```

> **Do not edit the generated `.html` files directly.** The next build overwrites
> them. Edit `tools/content.py` (copy, FAQs, metadata) or `tools/build.py`
> (layout, shared shell) and re-run the build.

The reason for this split: six converter pages share a header, footer, ad slots,
JSON-LD scaffolding and legal links. Hand-maintaining that across six files is
how nav links silently drift out of sync. One template, one content file, and
every page stays consistent by construction.

The FAQ structured data is generated from the same list as the visible FAQ
markup, so the two can never disagree — a common cause of Search Console
warnings.

## Adding a converter

Append a dictionary to `TOOLS` in `tools/content.py` and re-run the build. A new
directory, its sitemap entry, its hub card, its footer link and the "other
converters" cross-links on every existing page all appear automatically.

```python
{
    "slug": "png-to-avif",          # becomes /png-to-avif/
    "source": "png",                # key from SOURCE_FORMATS in converter.js
    "target": "avif",               # key from TARGET_FORMATS in converter.js
    "title": "...", "description": "...",
    "h1": "...", "lede": "...", "card": "...",
    "about_h2": "...", "about": ["<p>-level HTML allowed"],
    "why_h2": "...", "why": [("Bold lead.", "Rest of the sentence.")],
    "notes_h2": "...", "notes": ["..."],
    "faqs": [("Question?", "Plain-text answer.")],
},
```

A genuinely new **format** (rather than a new pairing of existing ones) also
needs an entry in `SOURCE_FORMATS` or `TARGET_FORMATS` in
`assets/js/converter.js` — including the magic-byte check that recognises it.

Write real, distinct copy for each page. Six pages of spun boilerplate is a
doorway-page pattern that AdSense reviewers reject and Google discounts.

## Deploy to GitHub Pages

Already configured: Settings → Pages → *Deploy from a branch* → `main` / `(root)`.

```bash
python3 tools/build.py
git add -A
git commit -m "Update converters"
git push
```

Every push to `main` redeploys automatically, in a minute or two.

### Custom domain

Already set up: the `CNAME` file at the repository root holds `convert-img.me`,
DNS points at GitHub's Pages IPs, and HTTPS is serving. To change domains, edit
`CNAME`, update `BASE_URL` (next section), rebuild, and update the DNS record.

## Configure the site URL

**One line, one place:** `BASE_URL` at the top of `tools/content.py`.

```python
BASE_URL = "https://convert-img.me"
```

Re-run the build and every canonical tag, Open Graph URL, sitemap entry,
manifest path, `robots.txt` line and absolute `404.html` link updates together.

`404.html` gets root-relative links derived from `BASE_URL`'s path (`/` on a
custom domain, `/image-tools/` on a project site), because GitHub Pages serves
it for missing paths at any depth and relative links would break.

`robots.txt` only takes effect at a domain root. On `convert-img.me` it does;
if you ever move back to a `github.io/<repo>/` path the generator adds a comment
noting it is inert there. Either way, submit `sitemap.xml` in Search Console.

## Add your Google AdSense code

Both steps are in `tools/build.py`, so a single edit applies to all ten pages.

**1. The loader.** In `ADSENSE_HEAD_COMMENT`, replace the comment with your tag:

```html
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-XXXXXXXXXXXXXXXX" crossorigin="anonymous"></script>
```

**2. The units.** Ad slots ship **commented out**, so nothing renders — visitors
and AdSense reviewers never see empty grey boxes, which read as an unfinished
template. Each generated page contains four blocks like this:

```html
  <!-- AD SLOT 1 (leaderboard)
       To activate: fill in the two IDs below, then remove this opening comment
       marker and the closing one after the </aside>.

  <aside class="ad-slot ad-slot--leaderboard wrap" aria-label="Advertisement">
    <ins class="adsbygoogle" ...></ins>
  </aside>

  -->
```

Edit the `ad_slot()` function in `tools/build.py` so it emits your real unit,
then rebuild — one edit covers all ten pages. Keep the `<aside class="ad-slot">`
wrapper, because that is what reserves the height:

```html
<ins class="adsbygoogle" style="display:block"
     data-ad-client="ca-pub-XXXXXXXXXXXXXXXX" data-ad-slot="XXXXXXXXXX"
     data-ad-format="auto" data-full-width-responsive="true"></ins>
<script>(adsbygoogle = window.adsbygoogle || []).push({});</script>
```

Then `python3 tools/build.py`. No publisher or slot IDs are invented anywhere in
this project — paste your own from your AdSense account.

Setting `AD_PLACEHOLDERS = True` in `tools/content.py` renders visible grey
boxes instead, which is useful for checking spacing while you work on the
layout. **Never deploy a build with that flag on.**

The desktop sidebar column only appears when a rail ad is actually present
(`.content-grid:has(.ad-slot--rail)`), so while the slots are commented out the
article centres itself instead of leaving a dead 300 px gutter. Uncommenting the
ad restores the two-column layout with no other change.

### The four slots on every page

| Slot | Position | Reserved height |
|---|---|---|
| 1 | Below the converter, above the article | 100 px mobile / 90 px desktop |
| 2 | In-content, mid-article | 250 px (hidden below 600 px wide) |
| 3 | Sticky desktop sidebar | 600 px (hidden below 1080 px wide) |
| 4 | Above the footer | 100 px mobile / 90 px desktop |

Nothing sits above the converter, beside its buttons, or between the user and a
download. Slot 2 is dropped on phones to keep mobile ad density low. Heights are
reserved so a late-loading ad cannot shift the layout, and every slot is
labelled "Advertisement".

To change a size, edit the `min-height` values under `AD SLOTS` in
`assets/css/styles.css`. To add or remove a slot, edit the page templates in
`build.py`; nothing else depends on them, and an ad that fails to load just
leaves an empty box.

## Update the SEO metadata

Titles, meta descriptions, headings and FAQs are all per-tool fields in
`tools/content.py`. Each page also emits JSON-LD for `WebApplication`, `HowTo`,
`BreadcrumbList` and `FAQPage`; the hub emits `WebSite` and `ItemList`. All of it
is generated, so it cannot drift from the visible content.

Social cards live at `assets/img/og-<slug>.png` (1200×630), one per tool.

Validate changes with the [Rich Results Test](https://search.google.com/test/rich-results).

## Search Console and Analytics

Both hook into `ADSENSE_HEAD_COMMENT` in `tools/build.py`:

```html
<meta name="google-site-verification" content="YOUR_TOKEN">
```

Rebuild, push, then press Verify and submit `https://convert-img.me/sitemap.xml`
under **Sitemaps**. Add `convert-img.me` as the property, not the github.io URL.

Analytics is deliberately absent so the site makes no third-party requests by
default. Paste your `gtag.js` snippet in the same place to enable it.

## How the converters work

All six pages run one engine. A page declares its formats in a JSON block:

```html
<script type="application/json" id="tool-config">{"source":"png","target":"jpeg"}</script>
```

From there:

1. **Validate.** Extension and MIME type first, then the file's magic bytes — a
   JPEG renamed to `.png` is rejected before it wastes a decode.
2. **Preview.** An object URL renders a thumbnail, which doubles as a decode test
   and supplies the original dimensions.
3. **Decode.** `createImageBitmap()` decodes off the main thread so large images
   do not freeze the page. Older Safari falls back to an `<img>` element.
4. **Encode.** Drawn to an `OffscreenCanvas` and encoded via `convertToBlob()`.
   For JPG the canvas is first filled with the chosen background colour, because
   JPEG has no alpha and transparent pixels would otherwise come out black.
   Lossy targets take the quality slider's value.
5. **Deliver.** Each result gets an object URL behind `<a download>`. *Download
   all as ZIP* builds a stored (uncompressed) archive in `zip.js` — image data is
   already compressed, so this costs nothing and avoids a dependency. PNG results
   also offer *Copy*, which writes the image to the system clipboard.

Encoder support is feature-detected at runtime by encoding a 1×1 pixel and
checking the MIME type that comes back, so a browser that cannot write WebP says
so instead of silently handing over a PNG with the wrong extension.

Files convert one at a time, yielding to the event loop between each, so the UI
stays responsive. Object URLs are revoked on remove, clear and unload.

**Nothing is uploaded.** There is no `fetch`, `XMLHttpRequest`, `WebSocket`,
`sendBeacon` or form submission anywhere in the converter code.

## Testing

The site is verified with a headless-Chromium suite that drives the real pages
in an iframe: 150 assertions covering all six converters end to end — output
magic bytes, decoded dimensions, transparency preserved on PNG/WebP output,
background fill on JPG output, the quality slider actually changing file size,
rejection of mislabelled files, the ZIP structure, the theme toggle persisting
across navigation, and confirmation that no request ever carries an image.

The harness lives outside the repository (it is a development tool, not part of
the deployed site). To re-run it, serve the site locally and point a headless
browser at a page that iframes each tool and drives it via `DataTransfer`.

## Limitations

Honest list, so you don't get surprise support email:

- **No HEIC support.** Browsers cannot decode HEIC natively; it would need a
  ~1 MB WebAssembly decoder on every page load. Deliberately omitted, and the
  hub FAQ explains why.
- **Animated WebP converts to its first frame only.** PNG and JPG hold a single
  image.
- **JPG output loses transparency.** Unavoidable — JPEG has no alpha channel. The
  background colour is user-selectable, and every JPG page says so.
- **Very large images can fail.** Anything over 16,384 px on a side is rejected
  up front with a clear message; mobile Safari's total-pixel cap is lower still.
  Failures are reported per file rather than producing a blank image.
- **JavaScript is required**, since conversion happens on the client. A
  `<noscript>` message explains this.
- **The contact address is obfuscated, not hidden.** It is assembled by a small
  script from `data-` attributes, so the raw HTML contains no usable `mailto:`
  string and the readable fallback is `sh.tasmi91 [at] gmail [dot] com`. This
  defeats naive harvesters; a scraper that executes JavaScript will still get it.
  A contact form would need a backend, which this site deliberately does not have.
- **The theme toggle writes one `localStorage` key** (`theme` = `light`/`dark`).
  This is disclosed explicitly in the privacy policy; nothing else is stored.
- **Colour management follows the browser.** Wide-gamut sources are converted to
  the browser's working colour space during decode.

## Licence

Yours to use and modify. WebP is a trademark of Google LLC; this project is not
affiliated with Google.
