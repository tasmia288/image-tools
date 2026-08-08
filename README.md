# WebP to PNG Converter

A free, static, client-side WebP → PNG converter. No backend, no build step, no
dependencies, no tracking. Images are decoded and re-encoded by the visitor's own
browser and never leave their device.

Built to be deployed on GitHub Pages for free and monetised with Google AdSense.

---

## Contents

- [Project layout](#project-layout)
- [Run it locally](#run-it-locally)
- [Build](#build)
- [Deploy to GitHub Pages](#deploy-to-github-pages)
- [Configure the site URL](#configure-the-site-url)
- [Add your Google AdSense code](#add-your-google-adsense-code)
- [Modify or move the ad placeholders](#modify-or-move-the-ad-placeholders)
- [Update the SEO metadata](#update-the-seo-metadata)
- [Google Search Console verification](#google-search-console-verification)
- [Google Analytics](#google-analytics)
- [How the converter works](#how-the-converter-works)
- [Limitations](#limitations)

---

## Project layout

```
.
├── index.html            Converter + all SEO content (the money page)
├── privacy.html          Privacy policy
├── terms.html            Terms of use & disclaimer
├── contact.html          Contact details
├── 404.html              Not-found page (uses absolute paths — see below)
├── robots.txt            Crawl rules + sitemap pointer
├── sitemap.xml           Four URLs, one per page
├── .nojekyll             Tells GitHub Pages to serve files as-is
└── assets/
    ├── css/styles.css    The entire stylesheet
    ├── js/app.js         UI: drop zone, file list, progress, downloads
    ├── js/converter.js   Validation, decoding, canvas → PNG encoding
    ├── js/zip.js         Minimal "Download all as ZIP" writer
    ├── js/year.js        Footer year for the non-app pages
    └── img/              favicon.svg, og-image.png (1200×630 social card)
```

Total page weight: roughly 40 KB of HTML/CSS/JS, plus zero third-party requests.

## Run it locally

The JavaScript uses ES modules, which browsers refuse to load over `file://`.
Serve the folder over HTTP instead — anything will do:

```bash
python3 -m http.server 8000
# then open http://localhost:8000
```

or

```bash
npx serve .
```

## Build

There is no build step. The files you edit are the files that get served. This is
deliberate: a build tool would add setup, CI and a failure mode without making a
four-page static site any faster.

## Deploy to GitHub Pages

This repository already points at `https://github.com/tasmia288/image-tools`.

```bash
git add .
git commit -m "Add WebP to PNG converter"
git push -u origin main
```

Then in the repository on GitHub: **Settings → Pages → Build and deployment**,
set **Source** to *Deploy from a branch*, **Branch** to `main`, folder `/ (root)`,
and press Save. The site goes live at:

```
https://tasmia288.github.io/image-tools/
```

The first deploy takes a minute or two. Every later `git push` to `main`
redeploys automatically.

### Using a custom domain

1. Add a file called `CNAME` at the repository root containing just your domain
   (e.g. `webptopngconverter.com`).
2. Point a `CNAME` DNS record at `tasmia288.github.io`, or four `A` records at
   GitHub's Pages IPs.
3. Enter the domain under **Settings → Pages → Custom domain** and tick
   *Enforce HTTPS*.
4. Update every URL as described in the next section.

## Configure the site URL

Absolute URLs are required for canonical tags, social cards and the sitemap.
They appear in these places — search and replace
`https://tasmia288.github.io/image-tools/` across the project:

| File | What to change |
|---|---|
| `index.html`, `privacy.html`, `terms.html`, `contact.html` | `<link rel="canonical">`, `og:url`, `og:image`, `twitter:image`, and the `url` field in the JSON-LD block in `index.html` |
| `sitemap.xml` | every `<loc>` |
| `robots.txt` | the `Sitemap:` line |
| `404.html` | the `/image-tools/` path prefix on each link (see below) |

**`404.html` is the exception to relative paths.** GitHub Pages serves it for any
missing URL at any depth, so its links must be absolute. If you move to a custom
domain or to a `<username>.github.io` user site, change `/image-tools/` to `/`
in that file.

**Note on `robots.txt`:** crawlers only read it at the domain root. On a project
site it lives at `tasmia288.github.io/image-tools/robots.txt`, which Google will
not fetch — the copy in this repo takes effect only on a custom domain or a user
site. Either way, submit `sitemap.xml` directly in Search Console.

## Add your Google AdSense code

Two steps, both marked with comments in the source.

**1. The loader script.** In the `<head>` of every page, find:

```html
<!-- GOOGLE ADSENSE LOADER -->
```

Replace the comment with your one-line snippet from AdSense:

```html
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-XXXXXXXXXXXXXXXX" crossorigin="anonymous"></script>
```

**2. The individual units.** `index.html` has four ad slots, each preceded by a
comment naming it (`AD SLOT 1` … `AD SLOT 4`). In each one, replace the
placeholder `<div>` with your `<ins>` unit — but keep the `<aside class="ad-slot">`
wrapper, because that is what reserves the height:

```html
<aside class="ad-slot ad-slot--leaderboard wrap" aria-label="Advertisement">
  <!-- was: <div class="ad-container">AD SLOT PLACEHOLDER</div> -->
  <ins class="adsbygoogle"
       style="display:block"
       data-ad-client="ca-pub-XXXXXXXXXXXXXXXX"
       data-ad-slot="XXXXXXXXXX"
       data-ad-format="auto"
       data-full-width-responsive="true"></ins>
  <script>(adsbygoogle = window.adsbygoogle || []).push({});</script>
</aside>
```

No publisher ID or slot ID is invented anywhere in this project — you must paste
your own from your AdSense account.

### Where the four slots are

| Slot | Location | Reserved height |
|---|---|---|
| 1 | Below the converter, above the article content | 100 px mobile / 90 px desktop |
| 2 | In-content, between "How to convert" and "Image quality" | 250 px (hidden below 600 px wide) |
| 3 | Sticky desktop sidebar beside the article | 600 px (hidden below 1080 px wide) |
| 4 | Above the footer, after the FAQ | 100 px mobile / 90 px desktop |

Nothing sits above the converter, beside its buttons, or between the user and a
download. Slot 2 is dropped on phones so mobile ad density stays low.

The legal pages carry no ad units, only the loader comment. Add units there only
if you want them.

## Modify or move the ad placeholders

Every slot is the same two-part structure:

```html
<aside class="ad-slot ad-slot--leaderboard" aria-label="Advertisement">
  <div class="ad-container">AD SLOT PLACEHOLDER</div>
</aside>
```

- `.ad-slot` adds the small "Advertisement" label above the unit and the vertical
  spacing that separates ads from the tool.
- `.ad-slot--leaderboard | --incontent | --rail` sets the reserved height. Change
  the `min-height` values in `styles.css` under the `AD SLOTS` heading if your
  units are a different size — matching them prevents layout shift.
- `.ad-container` is the box your `<ins>` replaces.

To add a slot, copy an `<aside>` anywhere in the page flow. To remove one, delete
the whole `<aside>`; nothing else depends on it. If an ad fails to load, the
reserved box simply stays empty and the tool is unaffected.

## Update the SEO metadata

Everything is in the `<head>` of each page, under the `SEO METADATA` comment:
title, meta description, canonical, Open Graph and Twitter tags.

`index.html` also carries a JSON-LD `@graph` with three schema types:
`WebApplication`, `HowTo` and `FAQPage`. **If you edit the FAQ text on the page,
edit the matching answer in the JSON-LD too** — Google penalises structured data
that does not match visible content. Validate changes with the
[Rich Results Test](https://search.google.com/test/rich-results).

The social card is `assets/img/og-image.png` (1200×630). Replace the file and
keep the name to avoid touching the meta tags.

## Google Search Console verification

Find this comment in the `<head>` of `index.html`:

```html
<!-- GOOGLE SEARCH CONSOLE VERIFICATION -->
```

Choose the *HTML tag* method in Search Console and paste the tag below it:

```html
<meta name="google-site-verification" content="YOUR_TOKEN_HERE">
```

Push, wait for the deploy, then press Verify. Afterwards submit
`https://tasmia288.github.io/image-tools/sitemap.xml` under **Sitemaps**.

The *HTML file* method also works: drop the `google*.html` file GitHub gives you
at the repository root.

## Google Analytics

Deliberately not included, so the site makes no third-party requests by default.
To add it, paste your `gtag.js` snippet under the `GOOGLE ANALYTICS` comment in
each page's `<head>`. Nothing in the converter depends on it.

## How the converter works

1. **Validate.** Each file is checked twice: by extension/MIME type, then by
   reading its first 12 bytes and confirming the RIFF container's form type is
   `WEBP`. A JPEG renamed to `.webp` is rejected with an explanation.
2. **Preview.** An object URL renders a thumbnail, which doubles as a decode test
   and supplies the original pixel dimensions.
3. **Decode.** `createImageBitmap()` decodes off the main thread, so a large image
   does not freeze the page. Older Safari falls back to an `<img>` element.
4. **Encode.** The bitmap is drawn to an `OffscreenCanvas` (or a regular canvas)
   with alpha enabled, then `convertToBlob()` / `toBlob()` produces PNG bytes.
   PNG is lossless and supports full alpha, so transparency survives.
5. **Download.** Each PNG gets its own object URL behind a `<a download>`.
   *Download all as ZIP* assembles a stored (uncompressed) ZIP in `zip.js` —
   PNG is already compressed, so this costs nothing and avoids a dependency.

Files are converted one at a time, yielding to the event loop between images, so
the interface stays responsive on long batches. Object URLs are revoked when a
file is removed, on *Clear all*, and on page unload.

**Nothing is uploaded.** There is no `fetch`, `XMLHttpRequest`, `WebSocket`,
`sendBeacon` or form submission anywhere in the code. Verified in the browser's
Network tab: converting an image produces zero network requests.

## Limitations

Honest list of what this cannot do, so you don't get surprise support email:

- **Animated WebP converts to its first frame only.** PNG holds a single image.
  (Stated on the page and in the FAQ.)
- **Very large images can fail.** Browsers cap canvas dimensions; anything over
  16,384 px on a side is rejected up front with a clear message, and mobile
  Safari's total-pixel cap is lower still. Failures are reported per file rather
  than silently producing a blank PNG.
- **PNG output is larger than the WebP input**, usually several times over. That
  is the format trade-off, not a bug — explained on the page.
- **JavaScript is required**, since the conversion happens on the client. A
  `<noscript>` message explains this.
- **Colour management follows the browser.** Wide-gamut source images are
  converted to the browser's working colour space during decode.
- **The header, footer and `<head>` are duplicated across the four pages.** With
  no build step there is no include mechanism. If you edit navigation or footer
  links, edit all four files. This was judged a better trade than introducing a
  static site generator for four pages.
- **`robots.txt` has no effect on a `github.io/<repo>/` project site** — see the
  note in [Configure the site URL](#configure-the-site-url).

## Licence

Yours to use and modify. WebP is a trademark of Google LLC; this project is not
affiliated with Google.
