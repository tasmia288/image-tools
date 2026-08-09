#!/usr/bin/env python3
"""Generates the static HTML for the image converter site.

Every page shares one shell (head, header, ad slots, footer) so navigation and
metadata cannot drift between them. Page content lives in content.py.

    python3 tools/build.py

Writes index.html, one directory per tool, the legal pages, 404.html and
sitemap.xml into the repository root. The output is plain static HTML — the
generator is an authoring convenience, not a deploy-time dependency.
"""

import html
import json
import pathlib
import sys
from urllib.parse import urlparse

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from content import (  # noqa: E402
    AD_PLACEHOLDERS, BASE_URL, COMMON_FAQS, CONTACT_EMAIL, LAST_MODIFIED, LAST_UPDATED,
    SITE_NAME, TOOLS,
)

ROOT = pathlib.Path(__file__).resolve().parent.parent
esc = html.escape

# Path component of BASE_URL, always with a trailing slash: "/" on a custom
# domain, "/image-tools/" on a github.io project site. Used by 404.html, which
# cannot use relative links because it is served for missing paths at any depth.
SITE_PATH = (urlparse(BASE_URL).path.rstrip("/") or "") + "/"


# ---------------------------------------------------------------------------
# Shared shell
# ---------------------------------------------------------------------------

BRAND_SVG = (
    '<svg class="brand-mark" width="28" height="28" viewBox="0 0 32 32" aria-hidden="true" focusable="false">'
    '<rect x="1.25" y="1.25" width="29.5" height="29.5" rx="8" fill="none" stroke="currentColor" stroke-width="2.5"/>'
    '<path d="M9 20.5 13.5 12l4.5 8.5" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>'
    '<circle cx="21.5" cy="12.5" r="2.25" fill="currentColor"/></svg>'
)

THEME_TOGGLE = (
    '<button type="button" class="theme-toggle" id="theme-toggle" aria-label="Switch colour theme">'
    '<svg class="icon-sun" width="18" height="18" viewBox="0 0 24 24" aria-hidden="true" focusable="false">'
    '<circle cx="12" cy="12" r="4.2" fill="none" stroke="currentColor" stroke-width="1.8"/>'
    '<path d="M12 2.5v2.2M12 19.3v2.2M2.5 12h2.2M19.3 12h2.2M5.2 5.2l1.6 1.6M17.2 17.2l1.6 1.6M18.8 5.2l-1.6 1.6M6.8 17.2l-1.6 1.6" '
    'stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>'
    '<svg class="icon-moon" width="18" height="18" viewBox="0 0 24 24" aria-hidden="true" focusable="false">'
    '<path d="M20 14.2A8.2 8.2 0 0 1 9.8 4a8.4 8.4 0 1 0 10.2 10.2z" fill="none" stroke="currentColor" '
    'stroke-width="1.8" stroke-linejoin="round"/></svg></button>'
)

# The inline theme script must run before first paint, otherwise a visitor who
# chose light mode on a dark-mode machine sees a flash of the wrong palette.
THEME_BOOTSTRAP = (
    '<script>(function(){try{var t=localStorage.getItem("theme");'
    'if(t==="light"||t==="dark")document.documentElement.dataset.theme=t}catch(e){}})();</script>'
)

ADSENSE_HEAD_COMMENT = """<!-- ==========================================================================
     GOOGLE ADSENSE LOADER
     After your site is approved, paste the single AdSense script tag here:
     <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-XXXXXXXXXXXXXXXX" crossorigin="anonymous"></script>
     Then fill in the individual .ad-slot containers in the page body.

     GOOGLE SEARCH CONSOLE VERIFICATION
     <meta name="google-site-verification" content="YOUR_TOKEN">

     GOOGLE ANALYTICS (optional)
     Paste your gtag.js snippet here. Omitted by default so the page makes
     zero third-party requests out of the box.
     ========================================================================== -->"""


def ad_slot(variant, number):
    """An advertising slot.

    With AD_PLACEHOLDERS off (the default, and what you should deploy) this
    emits a commented-out <aside> and nothing renders: no empty grey boxes for
    visitors or AdSense reviewers to see. Paste your publisher and slot IDs in,
    delete the two comment markers, and the unit goes live with its height
    already reserved.
    """
    wrapper_class = f"ad-slot ad-slot--{variant}"
    if variant == "leaderboard":
        wrapper_class += " wrap"

    if AD_PLACEHOLDERS:
        return f"""  <!-- AD SLOT {number} ({variant}) - development placeholder -->
  <aside class="{wrapper_class}" aria-label="Advertisement">
    <div class="ad-container">AD SLOT PLACEHOLDER</div>
  </aside>"""

    return f"""  <!-- AD SLOT {number} ({variant})
       To activate: fill in the two IDs below, then remove this opening comment
       marker and the closing one after the </aside>. Keep the <aside> wrapper —
       it reserves the slot's height so a late-loading ad cannot shift the page.

  <aside class="{wrapper_class}" aria-label="Advertisement">
    <ins class="adsbygoogle" style="display:block"
         data-ad-client="ca-pub-XXXXXXXXXXXXXXXX" data-ad-slot="XXXXXXXXXX"
         data-ad-format="auto" data-full-width-responsive="true"></ins>
    <script>(adsbygoogle = window.adsbygoogle || []).push({{}});</script>
  </aside>

  -->"""


def head(prefix, title, description, canonical, og_image, extra=""):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#0f172a" media="(prefers-color-scheme: dark)">
<meta name="theme-color" content="#ffffff" media="(prefers-color-scheme: light)">
{THEME_BOOTSTRAP}

<!-- ==========================================================================
     SEO METADATA - generated by tools/build.py from tools/content.py.
     Edit the content file and re-run the build rather than editing here.
     ========================================================================== -->
<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}">
<link rel="canonical" href="{canonical}">
<meta name="robots" content="index, follow, max-image-preview:large">

<meta property="og:type" content="website">
<meta property="og:site_name" content="{esc(SITE_NAME)}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{og_image}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:locale" content="en_US">

<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(title)}">
<meta name="twitter:description" content="{esc(description)}">
<meta name="twitter:image" content="{og_image}">

<link rel="icon" href="{prefix}assets/img/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="{prefix}assets/img/icon-192.png">
<link rel="manifest" href="{prefix}manifest.webmanifest">
<link rel="stylesheet" href="{prefix}assets/css/styles.css">

{ADSENSE_HEAD_COMMENT}
{extra}</head>
<body>
"""


def nav_links(prefix):
    """The same four links on every page. Uniform navigation matters both for
    visitors and for AdSense review, so no page gets a bespoke menu."""
    return [
        ("All tools", prefix or "./"),
        ("Privacy", f"{prefix}privacy.html"),
        ("Terms", f"{prefix}terms.html"),
        ("Contact", f"{prefix}contact.html"),
    ]


def header(prefix, current=None):
    links = "\n      ".join(
        f'<a href="{href}"{" aria-current=\"page\"" if label == current else ""}>{esc(label)}</a>'
        for label, href in nav_links(prefix)
    )
    return f"""<a class="skip-link" href="#main">Skip to the converter</a>

<header class="site-header">
  <div class="wrap header-inner">
    <a class="brand" href="{prefix or './'}" aria-label="{esc(SITE_NAME)}, home">
      {BRAND_SVG}
      <span class="brand-text">Image&nbsp;Tools</span>
    </a>
    <nav class="site-nav" aria-label="Primary">
      {links}
      {THEME_TOGGLE}
    </nav>
  </div>
</header>
"""


def footer(prefix):
    tool_links = "\n        ".join(
        f'<li><a href="{prefix}{t["slug"]}/">{esc(t["h1"].replace(" Converter", ""))}</a></li>' for t in TOOLS
    )
    return f"""<footer class="site-footer">
  <div class="wrap footer-inner">
    <div class="footer-brand">
      <strong>{esc(SITE_NAME)}</strong>
      <p>Free, private, browser-based image converters. No uploads, no accounts, no limits.</p>
    </div>
    <nav class="footer-nav" aria-label="Converters">
      <h2 class="footer-heading">Converters</h2>
      <ul>
        {tool_links}
      </ul>
    </nav>
    <nav class="footer-nav" aria-label="Legal">
      <h2 class="footer-heading">Site</h2>
      <ul>
        <li><a href="{prefix or './'}">All tools</a></li>
        <li><a href="{prefix}privacy.html">Privacy Policy</a></li>
        <li><a href="{prefix}terms.html">Terms &amp; Disclaimer</a></li>
        <li><a href="{prefix}contact.html">Contact</a></li>
      </ul>
    </nav>
  </div>
  <div class="wrap footer-bottom">
    <p>&copy; <span id="year">2026</span> {esc(SITE_NAME)}. Not affiliated with Google. WebP is a trademark of Google LLC.</p>
  </div>
</footer>

<script src="{prefix}assets/js/theme.js" defer></script>
"""


def jsonld(payload):
    return (
        '<script type="application/ld+json">\n'
        + json.dumps(payload, indent=2, ensure_ascii=False)
        + "\n</script>\n"
    )


def faq_block(faqs):
    """Visible FAQ markup. The JSON-LD is generated from the same list."""
    items = "\n".join(
        f"""          <details>
            <summary>{esc(q)}</summary>
            <p>{esc(a)}</p>
          </details>"""
        for q, a in faqs
    )
    return f"""        <div class="faq">
{items}
        </div>"""


def tool_grid(prefix, current_slug=None, limit=None):
    entries = [t for t in TOOLS if t["slug"] != current_slug]
    if limit:
        entries = entries[:limit]
    cards = "\n".join(
        f"""        <li><a href="{prefix}{t["slug"]}/">
          <span class="tool-name">{esc(t["h1"].replace(" Converter", ""))}</span>
          <span class="tool-desc">{esc(t["card"])}</span>
        </a></li>"""
        for t in entries
    )
    return f'      <ul class="tool-grid">\n{cards}\n      </ul>'


# ---------------------------------------------------------------------------
# Converter pages
# ---------------------------------------------------------------------------

def converter_card(tool):
    from_label = {"webp": "WebP", "png": "PNG", "jpeg": "JPG"}[tool["source"]]
    to_label = {"webp": "WebP", "png": "PNG", "jpeg": "JPG"}[tool["target"]]
    lossy = tool["target"] in ("jpeg", "webp")
    needs_background = tool["target"] == "jpeg"

    options = ""
    if lossy:
        rows = [
            f"""          <div class="option">
            <label for="quality">Quality</label>
            <input type="range" id="quality" name="quality" min="40" max="100" step="1" value="90">
            <output id="quality-value" for="quality">90%</output>
          </div>"""
        ]
        if needs_background:
            rows.append(
                """          <div class="option">
            <label for="background">Background</label>
            <input type="color" id="background" name="background" value="#ffffff">
            <span class="option-hint">JPG has no transparency, so transparent areas are filled with this colour.</span>
          </div>"""
            )
        options = f"""        <div class="options" id="options" hidden>
{chr(10).join(rows)}
        </div>
"""

    return f"""      <div class="tool-card">
        <!-- Drop zone. The visible button is a real <label> for the file input,
             so keyboard and screen-reader users get the same entry point. -->
        <div class="dropzone" id="dropzone">
          <svg class="dropzone-icon" width="44" height="44" viewBox="0 0 24 24" aria-hidden="true" focusable="false">
            <path d="M12 16V4m0 0L7.5 8.5M12 4l4.5 4.5" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M3.5 15v2.5A2.5 2.5 0 0 0 6 20h12a2.5 2.5 0 0 0 2.5-2.5V15" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
          </svg>
          <p class="dropzone-title">Drag &amp; drop {from_label} images here</p>
          <p class="dropzone-sub">or</p>

          <input type="file" id="file-input" class="visually-hidden" multiple aria-describedby="file-help">
          <label class="btn btn-primary" for="file-input">Choose {from_label} files</label>

          <p class="dropzone-hint" id="file-help">
            Accepted file type: <strong>.{ "jpg" if tool["source"] == "jpeg" else tool["source"] }</strong> &middot; Multiple files allowed &middot; Nothing is uploaded
          </p>
        </div>

{options}
        <!-- Live region: every status change is announced once, politely. -->
        <p class="status" id="status" role="status" aria-live="polite"></p>

        <div class="progress" id="progress" hidden>
          <div class="progress-bar" id="progress-bar" role="progressbar"
               aria-label="Conversion progress" aria-valuemin="0" aria-valuemax="100" aria-valuenow="0"></div>
        </div>

        <ul class="file-list" id="file-list" aria-label="Selected images"></ul>

        <div class="toolbar" id="toolbar" hidden>
          <button type="button" class="btn btn-primary" id="convert-btn">Convert to {to_label}</button>
          <button type="button" class="btn btn-secondary" id="download-all-btn" hidden>Download all as ZIP</button>
          <button type="button" class="btn btn-ghost" id="clear-btn">Clear all</button>
        </div>
      </div>"""


def build_tool_page(tool):
    prefix = "../"
    slug = tool["slug"]
    canonical = f"{BASE_URL}/{slug}/"
    og_image = f"{BASE_URL}/assets/img/og-{slug}.png"
    from_label = {"webp": "WebP", "png": "PNG", "jpeg": "JPG"}[tool["source"]]
    to_label = {"webp": "WebP", "png": "PNG", "jpeg": "JPG"}[tool["target"]]
    faqs = tool["faqs"] + COMMON_FAQS

    structured = jsonld({
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "WebApplication",
                "name": tool["h1"],
                "url": canonical,
                "applicationCategory": "MultimediaApplication",
                "operatingSystem": "Any modern web browser",
                "browserRequirements": "Requires JavaScript and HTML5 Canvas support",
                "description": tool["description"],
                "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
            },
            {
                "@type": "HowTo",
                "name": f"How to convert {from_label} to {to_label}",
                "totalTime": "PT1M",
                "step": [
                    {"@type": "HowToStep", "name": "Add your files",
                     "text": f"Drag {from_label} images onto the drop area, or use the Choose {from_label} files button to pick them from your device."},
                    {"@type": "HowToStep", "name": "Convert",
                     "text": f"Press Convert to {to_label}. Each image is decoded and re-encoded inside your browser."},
                    {"@type": "HowToStep", "name": "Download",
                     "text": f"Download each {to_label} individually, or use Download all as ZIP for several images at once."},
                ],
            },
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "All tools", "item": f"{BASE_URL}/"},
                    {"@type": "ListItem", "position": 2, "name": tool["h1"], "item": canonical},
                ],
            },
            {
                "@type": "FAQPage",
                "mainEntity": [
                    {"@type": "Question", "name": q,
                     "acceptedAnswer": {"@type": "Answer", "text": a}}
                    for q, a in faqs
                ],
            },
        ],
    })


    about = "\n        ".join(f"<p>{p}</p>" for p in tool["about"])
    why = "\n          ".join(f"<li><strong>{esc(lead)}</strong> {esc(rest)}</li>" for lead, rest in tool["why"])
    notes = "\n        ".join(f"<p>{p}</p>" for p in tool["notes"])
    config = json.dumps({"source": tool["source"], "target": tool["target"]})

    return "".join([
        head(prefix, tool["title"], tool["description"], canonical, og_image, structured),
        header(prefix),
        f"""
<main id="main">

  <!-- ===================== CONVERTER (the product) ===================== -->
  <section class="hero" id="converter" aria-labelledby="page-title">
    <div class="wrap">
      <nav class="crumbs" aria-label="Breadcrumb">
        <a href="{prefix}">All tools</a> <span aria-hidden="true">/</span> <span aria-current="page">{esc(from_label)} to {esc(to_label)}</span>
      </nav>
      <h1 id="page-title">{esc(tool["h1"])}</h1>
      <p class="lede">{esc(tool["lede"])}</p>

{converter_card(tool)}

      <p class="privacy-note">
        <svg width="16" height="16" viewBox="0 0 24 24" aria-hidden="true" focusable="false">
          <path d="M12 3l7 3v5.5c0 4.3-2.9 8.2-7 9.5-4.1-1.3-7-5.2-7-9.5V6l7-3z" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/>
          <path d="M9 12.2l2.1 2.1L15.2 10" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        Your images are processed directly in your browser and are not uploaded to our servers.
      </p>

      <noscript>
        <p class="alert">This converter needs JavaScript, because the conversion runs on your own device rather than on a server. Please enable JavaScript to use the tool.</p>
      </noscript>
    </div>
  </section>

{ad_slot("leaderboard", 1)}

  <div class="wrap content-grid">
    <div class="content-main">

      <section class="section" id="about" aria-labelledby="about-h">
        <h2 id="about-h">{esc(tool["about_h2"])}</h2>
        {about}
      </section>

      <section class="section" id="why" aria-labelledby="why-h">
        <h2 id="why-h">{esc(tool["why_h2"])}</h2>
        <ul class="reason-list">
          {why}
        </ul>
      </section>

      <section class="section" id="how-to" aria-labelledby="how-to-h">
        <h2 id="how-to-h">How to convert {esc(from_label)} to {esc(to_label)}</h2>
        <ol class="steps">
          <li>
            <h3>Add your images</h3>
            <p>Drag one or more {esc(from_label)} files onto the drop area at the top of this page, or press <strong>Choose {esc(from_label)} files</strong> to pick them from your device. Each file appears in the list with a preview, its original name, pixel dimensions and file size.</p>
          </li>
          <li>
            <h3>Convert</h3>
            <p>Press <strong>Convert to {esc(to_label)}</strong>. Your browser decodes each image, draws it to an HTML5 canvas and re-encodes it. Files are handled one at a time so the page stays responsive.</p>
          </li>
          <li>
            <h3>Download</h3>
            <p>Press <strong>Download {esc(to_label)}</strong> next to any finished image, or <strong>Download all as ZIP</strong> to grab everything at once. Filenames keep their original stem, with the extension changed.</p>
          </li>
        </ol>
      </section>

{ad_slot("incontent", 2)}

      <!-- id is "image-quality", not "quality": the quality slider owns that id. -->
      <section class="section" id="image-quality" aria-labelledby="image-quality-h">
        <h2 id="image-quality-h">{esc(tool["notes_h2"])}</h2>
        {notes}
      </section>

      <section class="section" id="privacy-section" aria-labelledby="privacy-h">
        <h2 id="privacy-h">Privacy: nothing is uploaded</h2>
        <p>
          Most online converters send your file to a server, process it there and hand back a download
          link. This one does not. The page is a static site with no backend and no upload endpoint —
          your images are read from disk by the browser, decoded by the browser and re-encoded by the
          browser. They stay on your device.
        </p>
        <p>
          A practical consequence: the tool keeps working offline once the page has loaded, and it is
          safe for images you would not want to hand to a third party. If you would like to verify the
          claim yourself, open your browser's developer tools, switch to the Network tab and run a
          conversion — you will see no request carrying your image. Read the full
          <a href="{prefix}privacy.html">privacy policy</a> for details on advertising cookies.
        </p>
      </section>

      <section class="section" id="faq" aria-labelledby="faq-h">
        <h2 id="faq-h">Frequently asked questions</h2>
{faq_block(faqs)}
      </section>

    </div>

{ad_slot("rail", 3)}
  </div>

  <section class="wrap related" aria-labelledby="related-h">
    <h2 id="related-h">Other converters</h2>
{tool_grid(prefix, current_slug=slug)}
  </section>

{ad_slot("leaderboard", 4)}

</main>

""",
        footer(prefix),
        f"""<script type="application/json" id="tool-config">{config}</script>
<script type="module" src="{prefix}assets/js/app.js"></script>
</body>
</html>
""",
    ])


# ---------------------------------------------------------------------------
# Hub page
# ---------------------------------------------------------------------------

def build_hub():
    prefix = ""
    canonical = f"{BASE_URL}/"
    title = "Free Online Image Converters - WebP, PNG and JPG (No Upload)"
    description = (
        "Free browser-based image converters for WebP, PNG and JPG. Batch convert, adjust quality, "
        "and download instantly. Your images are never uploaded to a server."
    )
    faqs = [
        ("Are my images uploaded to a server?", "No. Every converter here runs on your own device using your browser's image decoder and HTML5 Canvas. The site is static, with no backend and no upload endpoint, so there is nowhere for a file to be sent. You can confirm this in the Network tab of your browser's developer tools."),
        ("Are these converters free?", "Yes. There is no sign-up, no watermark and no daily quota. Running costs are covered by advertising, which is kept clearly labelled and separate from the tools."),
        ("Can I convert several images at once?", "Yes. Every converter accepts multiple files, processes them one at a time so the page stays responsive, and offers a single ZIP archive of the results."),
        ("Which formats are supported?", "Conversion between WebP, PNG and JPG in the combinations listed above. These are the formats every browser can both decode and encode natively, which is what makes instant, private, in-browser conversion possible."),
        ("Do these work on a phone?", "Yes. Every page is responsive and works in mobile Chrome, Safari, Firefox and Edge. Very large images may fail on phones because of tighter memory limits."),
        ("Why is there no HEIC converter?", "Browsers cannot decode HEIC natively, so an in-browser HEIC tool would need to download a large WebAssembly decoder. That would slow every page load, so it is deliberately not offered here."),
    ]

    structured = jsonld({
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "WebSite",
                "name": SITE_NAME,
                "url": canonical,
                "description": description,
            },
            {
                "@type": "ItemList",
                "name": "Image converters",
                "itemListElement": [
                    {"@type": "ListItem", "position": i + 1, "name": t["h1"], "url": f"{BASE_URL}/{t['slug']}/"}
                    for i, t in enumerate(TOOLS)
                ],
            },
            {
                "@type": "FAQPage",
                "mainEntity": [
                    {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
                    for q, a in faqs
                ],
            },
        ],
    })


    return "".join([
        head(prefix, title, description, canonical, f"{BASE_URL}/assets/img/og-image.png", structured),
        header(prefix),
        f"""
<main id="main">

  <section class="hero" aria-labelledby="page-title">
    <div class="wrap">
      <h1 id="page-title">Free Online Image Converters</h1>
      <p class="lede">
        Convert between WebP, PNG and JPG right in your browser. Free, unlimited, no sign-up —
        and your images never leave your device.
      </p>
      <div class="hub-grid">
{tool_grid(prefix)}
      </div>

      <p class="privacy-note">
        <svg width="16" height="16" viewBox="0 0 24 24" aria-hidden="true" focusable="false">
          <path d="M12 3l7 3v5.5c0 4.3-2.9 8.2-7 9.5-4.1-1.3-7-5.2-7-9.5V6l7-3z" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/>
          <path d="M9 12.2l2.1 2.1L15.2 10" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        Your images are processed directly in your browser and are not uploaded to our servers.
      </p>
    </div>
  </section>

{ad_slot("leaderboard", 1)}

  <div class="wrap content-grid">
    <div class="content-main">

      <section class="section" aria-labelledby="how-h">
        <h2 id="how-h">How these converters work</h2>
        <p>
          Every tool on this site does the same three things: it reads your file from disk, decodes it
          with the image decoder already built into your browser, and re-encodes the pixels to the
          format you asked for using an HTML5 canvas. All three steps happen on your own machine.
        </p>
        <p>
          That design has real consequences. There is no queue and no upload wait, so conversion takes
          about as long as opening the file. It keeps working after the page has loaded even if your
          connection drops. And because no server ever receives your images, there is no copy of them
          anywhere for anyone to leak, retain or scan.
        </p>
      </section>

      <section class="section" aria-labelledby="pick-h">
        <h2 id="pick-h">Which format should you choose?</h2>
        <ul class="reason-list">
          <li><strong>PNG</strong> is lossless. Choose it for logos, icons, screenshots of text, and anything you will edit repeatedly or that needs transparency. Photographs stored as PNG get very large.</li>
          <li><strong>JPG</strong> is the universal photographic format. Choose it when compatibility matters most — upload forms, print labs, older software — or when you need a photograph to be small and it has no transparency.</li>
          <li><strong>WebP</strong> is the modern web format. Choose it for images you are publishing online: roughly 25–35% smaller than JPEG at the same quality, with transparency support that JPEG lacks.</li>
        </ul>
      </section>

{ad_slot("incontent", 2)}

      <section class="section" id="faq" aria-labelledby="faq-h">
        <h2 id="faq-h">Frequently asked questions</h2>
{faq_block(faqs)}
      </section>

    </div>

{ad_slot("rail", 3)}
  </div>

{ad_slot("leaderboard", 4)}

</main>

""",
        footer(prefix),
        "</body>\n</html>\n",
    ])


# ---------------------------------------------------------------------------
# Static pages
# ---------------------------------------------------------------------------

def build_page(slug, title, description, heading, subtitle, body, current=None):
    prefix = ""
    canonical = f"{BASE_URL}/{slug}"
    extra = ""
    return "".join([
        head(prefix, title, description, canonical, f"{BASE_URL}/assets/img/og-image.png", extra),
        header(prefix, current),
        f"""
<main id="main" class="wrap">
  <div class="page-header">
    <h1>{esc(heading)}</h1>
    <p class="updated">{subtitle}</p>
  </div>

  <article class="prose">
{body}
  </article>
</main>

""",
        footer(prefix),
        "</body>\n</html>\n",
    ])


PRIVACY_BODY = f"""    <div class="callout">
      <p><strong>The short version.</strong> Images you convert on this site never leave your device. The conversion runs inside your browser, and there is no server that could receive a file. We do not ask for an account, and we do not collect names, email addresses or images.</p>
    </div>

    <h2>Who we are</h2>
    <p>This site is a free collection of single-purpose image conversion tools. It is operated by an individual, not a company. You can reach us through the <a href="contact.html">contact page</a>.</p>

    <h2>Your images</h2>
    <p>When you add a file to any converter here, your browser reads it from your device into the page's own memory. Decoding and encoding are performed by your browser's built-in image APIs. No copy of the file is transmitted anywhere, because the site is a static page with no backend, no upload endpoint and no storage.</p>
    <p>Files stay in memory only while the page is open. Closing or reloading the tab discards them, and removing a file with the remove button or <em>Clear all</em> releases it immediately. Nothing is written to your device unless you explicitly press a download button.</p>
    <p>You can verify this yourself: open your browser's developer tools, switch to the Network tab, and convert an image. No request carrying your file will appear.</p>

    <h2>Hosting and server logs</h2>
    <p>The site is hosted as static files on GitHub Pages. Like virtually every web host, GitHub's infrastructure records standard technical request data — IP address, user agent, requested URL and timestamp — for security and abuse prevention. We do not control, receive, or have access to those logs. See <a href="https://docs.github.com/site-policy/privacy-policies/github-privacy-statement" rel="nofollow noopener" target="_blank">GitHub's Privacy Statement</a> for details.</p>

    <h2>Cookies and local storage</h2>
    <p>The converters set no cookies and use no tracking identifiers.</p>
    <p>One small exception is worth naming precisely: if you use the light/dark theme button, your choice is saved in your browser's <code>localStorage</code> under the key <code>theme</code>, holding the single word "light" or "dark". It never leaves your device, is not an identifier, is not readable by anyone else, and is not used for analytics or advertising. Clearing your browser data removes it. If you never touch the toggle, nothing is stored at all.</p>
    <p>Any other cookies present on this site come from advertising, described below.</p>

    <h2>Advertising</h2>
    <p>This site is free to use and is supported by advertising. Where advertising is enabled, we use Google AdSense.</p>
    <ul>
      <li>Third-party vendors, including Google, use cookies to serve ads based on your prior visits to this and other websites.</li>
      <li>Google's use of advertising cookies enables it and its partners to serve ads to you based on your visit to this site and other sites on the internet.</li>
      <li>You can opt out of personalised advertising by visiting <a href="https://www.google.com/settings/ads" rel="nofollow noopener" target="_blank">Google Ads Settings</a>, or opt out of third-party vendor cookies for personalised advertising at <a href="https://www.aboutads.info/choices/" rel="nofollow noopener" target="_blank">aboutads.info/choices</a>.</li>
      <li>Advertising partners never receive your images. Ads are rendered in separate, clearly labelled containers and have no access to the files in the converter.</li>
    </ul>
    <p>If you are in the European Economic Area, the United Kingdom or Switzerland, a consent notice is presented before personalised advertising cookies are set, as required by Google's EU user consent policy.</p>

    <h2>Analytics</h2>
    <p>If web analytics are enabled on this site, they are used only in aggregate to understand which pages are visited and from where. Analytics never receive your images or filenames.</p>

    <h2>Children</h2>
    <p>This site is not directed at children under 13 and does not knowingly collect personal information from them.</p>

    <h2>Your rights</h2>
    <p>Because we do not collect or store personal data ourselves, there is generally nothing for us to access, correct or delete on your behalf. For data held by our advertising or hosting providers, please use the links above to exercise your choices with them directly. If you have a question, <a href="contact.html">get in touch</a>.</p>

    <h2>Changes to this policy</h2>
    <p>This policy may be updated as the site changes — for example if advertising or analytics are added or removed. The date at the top of the page reflects the most recent revision.</p>"""


TERMS_BODY = """    <div class="callout">
      <p>By using this website you agree to the terms below. If you do not agree with them, please do not use the site.</p>
    </div>

    <h2>The service</h2>
    <p>This site provides free, browser-based tools that convert images between WebP, PNG and JPG. Conversion runs entirely on your own device using your browser's image APIs. No account is required, and no fee is charged.</p>

    <h2>Acceptable use</h2>
    <ul>
      <li>You may use these converters for personal or commercial purposes, without attribution.</li>
      <li>You are solely responsible for the images you convert, including having the right to use and modify them.</li>
      <li>Do not use the site to process material that is unlawful in your jurisdiction, or that infringes someone else's copyright or privacy.</li>
      <li>Do not attempt to disrupt the site, or to redistribute it in a way that misrepresents its origin.</li>
    </ul>

    <h2>No warranty</h2>
    <p>The site is provided "as is" and "as available", without warranty of any kind, express or implied, including but not limited to merchantability, fitness for a particular purpose and non-infringement. We do not warrant that the converters will be uninterrupted, error-free, or that every image will convert successfully. Conversion depends on your browser, your device's available memory and the contents of the file, and some images — very large ones in particular — may fail.</p>

    <h2>Keep your originals</h2>
    <p>Always keep a copy of your original files. The converters produce new files and never modify or delete the source image, but you should not rely on this site as storage or as your only copy of anything. Converted output is held only in your browser's memory and is lost when you close the page.</p>

    <h2>Limitation of liability</h2>
    <p>To the fullest extent permitted by law, the operator of this site shall not be liable for any indirect, incidental, special or consequential damages, or for any loss of data, profits or goodwill, arising out of your use of or inability to use the site — even if advised of the possibility of such damages.</p>

    <h2>Advertising and third-party links</h2>
    <p>The site is supported by advertising, which may be provided by Google AdSense. Advertisements are displayed in clearly labelled containers, separate from the tools' controls. We do not endorse and are not responsible for the content of advertisements or of any third-party site they link to. See the <a href="privacy.html">privacy policy</a> for how advertising cookies are handled.</p>

    <h2>Intellectual property</h2>
    <p>The site's design, text and source code belong to their author. Your images remain entirely yours — we obtain no rights over anything you convert, and we never receive a copy of it in the first place.</p>
    <p>WebP is a trademark of Google LLC. This site is not affiliated with, endorsed by, or sponsored by Google.</p>

    <h2>Changes</h2>
    <p>These terms may be revised from time to time. Continued use of the site after a change constitutes acceptance of the revised terms. The date at the top of this page reflects the most recent revision.</p>

    <h2>Contact</h2>
    <p>Questions about these terms? Use the <a href="contact.html">contact page</a>.</p>"""


EMAIL_USER, EMAIL_DOMAIN = CONTACT_EMAIL.split("@")
EMAIL_DOMAIN_SPACED = EMAIL_DOMAIN.replace(".", " [dot] ")

CONTACT_BODY = f"""    <div class="callout">
      <p>Email us at
        <!-- CHANGE ME: set CONTACT_EMAIL in tools/content.py and re-run the build.
             The address is assembled by script so harvesters scraping the raw
             HTML do not find a usable mailto: string. Without JavaScript the
             readable form below still tells a human where to write. -->
        <a class="contact-link" id="contact-email" href="#contact-email"
           data-user="{EMAIL_USER}" data-domain="{EMAIL_DOMAIN}"
           >{EMAIL_USER} [at] {EMAIL_DOMAIN_SPACED}</a>
        <script>
        (function () {{
          var a = document.getElementById('contact-email');
          if (!a) return;
          var address = a.dataset.user + String.fromCharCode(64) + a.dataset.domain;
          a.href = 'mailto:' + address;
          a.textContent = address;
        }})();
        </script>
      </p>
      <p>There is no contact form here, and that is deliberate: a form would need a server to receive it, and this site intentionally has no backend at all.</p>
    </div>

    <h2>What to get in touch about</h2>
    <ul>
      <li><strong>A file that will not convert.</strong> Tell us your browser and version, your operating system, and the image's dimensions and file size. Please do not attach the image unless you are happy to share it.</li>
      <li><strong>Bugs and layout problems.</strong> A screenshot and the device you saw it on are usually enough for us to reproduce the issue.</li>
      <li><strong>Accessibility.</strong> If something is hard to reach by keyboard or unclear with a screen reader, we want to hear about it and will treat it as a bug.</li>
      <li><strong>Feature requests.</strong> Other formats, batch options, or anything that would save you a step.</li>
      <li><strong>Privacy and advertising questions.</strong> See the <a href="privacy.html">privacy policy</a> first — it may already answer you.</li>
    </ul>

    <h2>Before you write</h2>
    <p>Three things account for most reports:</p>
    <ul>
      <li><strong>The file is not really the format its name claims.</strong> Images renamed to a different extension are rejected on purpose. The tool tells you when the contents do not match.</li>
      <li><strong>The image is too large for the device.</strong> Browsers cap canvas size, and phones cap it lower than desktops. A very large image may convert on a laptop but fail on a phone.</li>
      <li><strong>Transparency disappeared.</strong> That is expected when converting to JPG, which has no alpha channel. Convert to PNG or WebP instead.</li>
    </ul>

    <h2>A note on your images</h2>
    <p>We never receive the images you convert — they are processed on your device and never uploaded. That also means we cannot look up or recover anything you converted. If you email us a file for debugging, you are sending it to us yourself, by choice.</p>

    <p><a href="./">← Back to all converters</a></p>"""


def build_404():
    links = "\n      ".join(
        f'<li><a href="{SITE_PATH}{t["slug"]}/">{esc(t["h1"])}</a></li>' for t in TOOLS
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
{THEME_BOOTSTRAP}
<title>Page not found - {esc(SITE_NAME)}</title>
<meta name="description" content="That page does not exist. Head back to the free image converters.">
<meta name="robots" content="noindex, follow">
<link rel="icon" href="{SITE_PATH}assets/img/favicon.svg" type="image/svg+xml">
<!-- GitHub Pages serves 404.html for any missing path at any depth, so these
     links are root-relative rather than relative. Generated from BASE_URL. -->
<link rel="stylesheet" href="{SITE_PATH}assets/css/styles.css">
</head>
<body>

<header class="site-header">
  <div class="wrap header-inner">
    <a class="brand" href="{SITE_PATH}" aria-label="{esc(SITE_NAME)}, home">
      {BRAND_SVG}
      <span class="brand-text">Image&nbsp;Tools</span>
    </a>
  </div>
</header>

<main id="main" class="wrap">
  <div class="page-header">
    <h1>Page not found</h1>
  </div>
  <article class="prose">
    <p>The page you asked for does not exist — it may have been renamed, or the link may be mistyped.</p>
    <ul>
      {links}
      <li><a href="{SITE_PATH}">All tools</a></li>
      <li><a href="{SITE_PATH}contact.html">Contact</a></li>
    </ul>
  </article>
</main>

</body>
</html>
"""


def build_sitemap():
    urls = [(f"{BASE_URL}/", "1.0", "monthly")]
    urls += [(f"{BASE_URL}/{t['slug']}/", "0.9", "monthly") for t in TOOLS]
    urls += [
        (f"{BASE_URL}/privacy.html", "0.3", "yearly"),
        (f"{BASE_URL}/terms.html", "0.3", "yearly"),
        (f"{BASE_URL}/contact.html", "0.3", "yearly"),
    ]
    entries = "\n".join(
        f"""  <url>
    <loc>{loc}</loc>
    <lastmod>{LAST_MODIFIED}</lastmod>
    <changefreq>{freq}</changefreq>
    <priority>{priority}</priority>
  </url>"""
        for loc, priority, freq in urls
    )
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<!-- Generated by tools/build.py. Update BASE_URL in tools/content.py to change these. -->
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{entries}
</urlset>
"""


def build_robots():
    at_root = SITE_PATH == "/"
    caveat = "" if at_root else (
        "# Note: crawlers only read robots.txt at the domain root. This site is served\n"
        "# from a subpath, so this file has no effect; submit the sitemap in Search\n"
        "# Console instead.\n"
    )
    return f"""# robots.txt - {SITE_NAME}
{caveat}
User-agent: *
Allow: /

# Ad crawlers need explicit access for AdSense to serve relevant ads.
User-agent: Mediapartners-Google
Allow: /

User-agent: AdsBot-Google
Allow: /

Sitemap: {BASE_URL}/sitemap.xml
"""


def build_manifest():
    return json.dumps({
        "name": SITE_NAME,
        "short_name": "Image Tools",
        "description": "Free browser-based converters for WebP, PNG and JPG. Nothing is uploaded.",
        "start_url": f"{BASE_URL}/",
        "scope": f"{BASE_URL}/",
        "display": "standalone",
        "background_color": "#0e131b",
        "theme_color": "#2f6df0",
        "icons": [
            {"src": f"{BASE_URL}/assets/img/icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any"},
            {"src": f"{BASE_URL}/assets/img/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any"},
            {"src": f"{BASE_URL}/assets/img/icon-maskable.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
        ],
    }, indent=2) + "\n"


# ---------------------------------------------------------------------------

def write(path, text):
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")
    print(f"  {path} ({len(text):,} bytes)")


def main():
    print("Building site…")
    write("index.html", build_hub())
    for tool in TOOLS:
        write(f"{tool['slug']}/index.html", build_tool_page(tool))
    write("privacy.html", build_page(
        "privacy.html", f"Privacy Policy - {SITE_NAME}",
        "How this site handles your data: images are converted locally in your browser and are never uploaded. Details on cookies, advertising and analytics.",
        "Privacy Policy", f"Last updated: {LAST_UPDATED}", PRIVACY_BODY, current="Privacy"))
    write("terms.html", build_page(
        "terms.html", f"Terms of Use & Disclaimer - {SITE_NAME}",
        "Terms of use and disclaimer for these free image converters: acceptable use, warranty disclaimer and limitation of liability.",
        "Terms of Use & Disclaimer", f"Last updated: {LAST_UPDATED}", TERMS_BODY, current="Terms"))
    write("contact.html", build_page(
        "contact.html", f"Contact - {SITE_NAME}",
        "Get in touch about these free image converters: bug reports, feature requests, accessibility issues and privacy questions.",
        "Contact", "We read every message, and reply to most within a few days.", CONTACT_BODY, current="Contact"))
    write("404.html", build_404())
    write("sitemap.xml", build_sitemap())
    write("robots.txt", build_robots())
    write("manifest.webmanifest", build_manifest())
    print(f"Done. {len(TOOLS)} converter pages + 5 supporting pages.")


if __name__ == "__main__":
    main()
