"""Per-page content for the image converter site.

Everything unique to a page lives here: headings, prose, FAQs and metadata.
`build.py` wraps this in the shared shell. Edit this file, then run:

    python3 tools/build.py

See the "Adding a converter" section of the top-level README.
"""

# --------------------------------------------------------------------------
# Site-wide settings. Change BASE_URL when you move to a custom domain.
# --------------------------------------------------------------------------
# No trailing slash. Must match the CNAME file at the repository root.
BASE_URL = "https://convert-img.me"
SITE_NAME = "Image Converter Tools"
CONTACT_EMAIL = "sh.tasmi91@gmail.com"

# Ad slots render as commented-out HTML by default, so visitors (and AdSense
# reviewers) never see empty grey boxes. Flip to True only while working on the
# layout locally — never in a build you deploy.
AD_PLACEHOLDERS = False
LAST_UPDATED = "9 August 2026"
LAST_MODIFIED = "2026-08-09"

# --------------------------------------------------------------------------
# Converter pages
# --------------------------------------------------------------------------
# Keys used by build.py:
#   slug, source, target        - engine wiring (must match converter.js keys)
#   title, description          - <title> and meta description
#   h1, lede                    - visible page heading and intro line
#   card                        - one-liner used on the hub grid and footer
#   about_h2, about             - "what is X" style section (list of paragraphs)
#   why_h2, why                 - bulleted reasons, (lead, rest) tuples
#   notes_h2, notes             - quality / file-size expectations
#   faqs                        - (question, answer) pairs, answers are plain text

TOOLS = [
    {
        "slug": "webp-to-png",
        "source": "webp",
        "target": "png",
        "title": "WebP to PNG Converter - Free Online Tool (No Upload)",
        "description": (
            "Convert WebP to PNG online for free. Drag and drop one or many WebP images and "
            "download PNG files instantly. Conversion runs in your browser, so images are never uploaded."
        ),
        "h1": "WebP to PNG Converter",
        "lede": (
            "Convert WebP images to PNG right here in your browser. Free, unlimited, no sign-up, "
            "and your files never leave your device."
        ),
        "card": "Turn WebP images into lossless PNG files that open in any application.",
        "about_h2": "What is WebP?",
        "about": [
            "WebP is an image format developed by Google and released in 2010. It supports both lossy and "
            "lossless compression, transparency and animation, and it typically produces files noticeably "
            "smaller than an equivalent JPEG or PNG. Because page weight affects search ranking and bounce "
            "rate, most content management systems, CDNs and e-commerce platforms now serve WebP "
            "automatically, which is why so many images you save from the web arrive with a "
            "<code>.webp</code> extension.",
            "Every current browser can display WebP. The friction shows up outside the browser: plenty of "
            "desktop software, printers, older operating systems and upload forms still expect a more "
            "traditional format.",
        ],
        "why_h2": "Why convert WebP to PNG?",
        "why": [
            ("Software compatibility.", "Older versions of Photoshop, Illustrator, Office and many print or CAD tools cannot open WebP without a plugin. PNG opens everywhere."),
            ("Upload restrictions.", "Job boards, government portals, marketplaces and print services frequently reject anything that is not PNG or JPEG."),
            ("Lossless editing.", "PNG is a lossless container, so repeated save cycles while you retouch an image will not add further compression artefacts."),
            ("Transparency that travels.", "Logos and cut-outs keep their alpha channel in PNG, which is the format most design and presentation tools expect for transparent assets."),
            ("Documents and slide decks.", "Word, PowerPoint, Google Slides and PDF workflows handle PNG far more predictably than WebP."),
            ("Archiving.", "PNG has been a stable, widely implemented standard since 1996, which makes it a safer long-term storage choice."),
        ],
        "notes_h2": "What happens to image quality and file size",
        "notes": [
            "Writing PNG is a lossless operation: every pixel the browser decoded from the WebP is stored "
            "exactly. What conversion cannot do is undo compression that already happened. If the original "
            "was a lossy WebP, the detail its encoder discarded is gone for good, and the PNG faithfully "
            "reproduces the slightly softened result rather than the original photograph.",
            "Expect the PNG to be <strong>larger</strong> than the WebP it came from, often by several times. "
            "That is not a fault in the conversion; it is the trade-off between a modern lossy codec and a "
            "lossless one. If small file size matters more than compatibility, keep the WebP.",
        ],
        "faqs": [
            ("How do I convert WebP to PNG?", "Add your WebP files to the drop area at the top of this page, press Convert to PNG, then download the results. The whole process runs in your browser and usually takes a second or two per image."),
            ("Is this WebP to PNG converter free?", "Yes. There is no sign-up, no watermark and no daily quota. Running costs are covered by advertising, which is kept clearly labelled and separate from the tool controls."),
            ("Does converting WebP to PNG reduce image quality?", "The PNG step is lossless, so nothing is lost in conversion. However, if the source was a lossy WebP, the artefacts already baked into it remain — converting cannot restore detail that the WebP encoder discarded."),
            ("Why is my PNG bigger than the WebP file?", "That is expected. WebP compresses photographic content much more aggressively than PNG. PNG is lossless, so it stores every pixel exactly and the file is usually several times larger."),
            ("Does the converter keep transparency?", "Yes. WebP images with an alpha channel are drawn onto a transparent canvas, and PNG supports full alpha, so transparent areas survive the conversion."),
            ("Can it convert animated WebP files?", "Only the first frame. PNG is a single-frame format, so an animated WebP converts to a still image."),
            ("Can I bulk convert WebP to PNG?", "Yes. Add as many files as you like and press convert once. They are processed one after another so the page stays responsive, and Download all as ZIP collects the results in a single archive."),
        ],
    },
    {
        "slug": "webp-to-jpg",
        "source": "webp",
        "target": "jpeg",
        "title": "WebP to JPG Converter - Free Online Tool (No Upload)",
        "description": (
            "Convert WebP to JPG online for free. Adjustable quality, batch conversion and instant "
            "downloads. Everything runs in your browser, so your images are never uploaded to a server."
        ),
        "h1": "WebP to JPG Converter",
        "lede": (
            "Convert WebP images to JPG in your browser, with control over quality and background. "
            "Free, unlimited, and nothing is uploaded."
        ),
        "card": "Convert WebP images to widely compatible JPG files, with adjustable quality.",
        "about_h2": "What is WebP, and why does JPG still matter?",
        "about": [
            "WebP is Google's modern image format. It compresses better than JPEG at similar visual quality, "
            "which is why so many websites now serve it — and why images you save from the web so often land "
            "on your disk as <code>.webp</code>.",
            "JPEG, by contrast, has been the default photographic format since 1992. Nearly three decades of "
            "ubiquity means every camera, printer, photo kiosk, email client and upload form understands it. "
            "When something refuses your WebP file, JPG is almost always the format it wants instead.",
        ],
        "why_h2": "Why convert WebP to JPG?",
        "why": [
            ("Upload forms reject WebP.", "Passport and visa portals, job applications, insurance claims and school systems very often accept JPEG only."),
            ("Photo printing.", "Print labs and photo-book services are built around JPEG, and many will not accept a WebP upload at all."),
            ("Smaller than PNG.", "If you need compatibility but the image is a photograph, JPG keeps the file far smaller than a lossless PNG would."),
            ("Older software.", "Legacy image viewers, some TV and camera slideshows, and older versions of Office open JPEG without complaint."),
            ("Email and messaging.", "JPEG attachments preview correctly everywhere, including older mail clients that show WebP as a broken file."),
        ],
        "notes_h2": "Quality, transparency and file size",
        "notes": [
            "JPEG is a lossy format, so this conversion re-compresses the image. Use the quality slider above "
            "the file list to choose the trade-off: 92% is a good default that is visually indistinguishable "
            "for most photographs, while dropping to 70–80% noticeably shrinks the file. Because the source "
            "WebP was very likely lossy too, you are compressing already-compressed data — keep quality high "
            "if the image will be edited or printed later.",
            "<strong>JPEG cannot store transparency.</strong> If your WebP has transparent areas, they have to "
            "be filled with something, so the converter composites the image onto a solid background colour "
            "first. White is the default; use the background picker to change it. Without this step "
            "transparent pixels would come out black.",
            "Animated WebP files convert to a still JPG of the first frame, since JPEG holds a single image.",
        ],
        "faqs": [
            ("How do I convert WebP to JPG?", "Drop your WebP files onto the area at the top of this page, pick a quality level if you want something other than the default, press Convert to JPG, and download the results."),
            ("Is converting WebP to JPG lossless?", "No. JPEG is a lossy format by design, so some data is discarded during encoding. At the default 92% quality the difference is invisible to the eye in normal viewing, but it is not a pixel-perfect copy. Convert to PNG instead if you need lossless output."),
            ("What happens to transparent areas?", "They are filled with the background colour shown in the options row, white by default, because JPEG has no alpha channel. If you need transparency preserved, convert to PNG or WebP instead."),
            ("What quality setting should I use?", "92% suits almost everything. Use 95–100% for images you will edit or print, and 70–80% when you want the smallest file for the web and can accept slight softening around edges and fine detail."),
            ("Will the JPG be smaller than the WebP?", "Usually not. WebP typically beats JPEG by 25–35% at matched quality, so a converted JPG is often somewhat larger. You are converting for compatibility, not for size."),
            ("Can I convert several WebP files at once?", "Yes. Add as many as you like, convert them in one pass, and use Download all as ZIP to get them in a single archive."),
            ("Are my images uploaded anywhere?", "No. The conversion uses your browser's own image decoder and canvas. This site is static, has no backend and no upload endpoint, so there is nowhere for a file to be sent."),
        ],
    },
    {
        "slug": "png-to-jpg",
        "source": "png",
        "target": "jpeg",
        "title": "PNG to JPG Converter - Free Online Tool (No Upload)",
        "description": (
            "Convert PNG to JPG online for free and shrink oversized screenshots and photos. "
            "Adjustable quality, batch conversion, and images never leave your browser."
        ),
        "h1": "PNG to JPG Converter",
        "lede": (
            "Convert PNG images to JPG and cut their file size dramatically. Runs entirely in your "
            "browser — free, unlimited, nothing uploaded."
        ),
        "card": "Shrink oversized PNG screenshots and photos into compact JPG files.",
        "about_h2": "Why PNG files get so large",
        "about": [
            "PNG is lossless: it reproduces every pixel exactly, with no compression artefacts anywhere. That "
            "is ideal for logos, icons, diagrams and screenshots of text, where crisp edges matter and the "
            "image uses a limited palette.",
            "It works far less well for photographs. A photo has fine gradients and noise in every pixel, and "
            "lossless compression has almost nothing repeatable to exploit — so a PNG photo can easily be "
            "five to ten times larger than the same picture as a JPEG. Since screenshots on both macOS and "
            "Windows are saved as PNG by default, most people accumulate large PNG files without ever "
            "choosing the format.",
        ],
        "why_h2": "Why convert PNG to JPG?",
        "why": [
            ("Attachment and upload limits.", "Email providers and web forms cap file size. Converting a 6 MB PNG screenshot to JPG typically brings it under 1 MB."),
            ("Faster websites.", "Photographic content served as PNG wastes bandwidth and hurts Core Web Vitals. JPEG is the right format for photographs."),
            ("Storage and backups.", "A folder of PNG photos consumes several times the space of the same images as JPEG."),
            ("Platform requirements.", "Some marketplaces, print services and ID-document portals accept JPEG only."),
            ("Sharing.", "Messaging apps and social platforms recompress everything anyway; sending JPEG avoids an extra lossy round trip on a needlessly large upload."),
        ],
        "notes_h2": "What you gain and what you give up",
        "notes": [
            "The size reduction is usually dramatic for photographs and much smaller for flat graphics — a "
            "logo or a screenshot of mostly text may barely shrink, and can even grow, because JPEG is poor "
            "at hard edges. If your PNG is a diagram, screenshot of text, or line art, converting to JPG is "
            "often the wrong move: you will add visible fuzz around the edges for little or no saving.",
            "<strong>Transparency is lost.</strong> JPEG has no alpha channel, so transparent regions are "
            "composited onto a solid colour before encoding — white by default, changeable in the options "
            "row. A transparent logo converted to JPG comes out on a white rectangle.",
            "The conversion is lossy and one-way. Keep the PNG if you may need to edit the image later; "
            "re-saving a JPEG repeatedly compounds compression damage.",
        ],
        "faqs": [
            ("How do I convert PNG to JPG?", "Add your PNG files to the drop area, choose a quality level if you want to, press Convert to JPG, then download each result or grab them all as a ZIP."),
            ("How much smaller will the JPG be?", "For photographs, typically 70–90% smaller. For screenshots of text, logos and diagrams the saving is much smaller and occasionally negative, because JPEG handles sharp edges poorly."),
            ("Will converting PNG to JPG lose quality?", "Yes, some. JPEG is lossy, so fine detail is approximated. At the default 92% the loss is invisible in normal viewing, but it is real and permanent — keep your original PNG."),
            ("What happens to a transparent PNG?", "The transparent areas are filled with the background colour from the options row, white by default. JPEG cannot store transparency, so there is no way to preserve it in this format."),
            ("Can I convert many PNG files at once?", "Yes. Batch conversion is supported, files are processed one at a time so the page stays responsive, and Download all as ZIP gives you a single archive."),
            ("Should I use JPG or WebP instead?", "If the destination is a modern website, WebP is smaller than JPEG at the same quality and supports transparency. Choose JPG when maximum compatibility matters more."),
            ("Are my PNG files uploaded to a server?", "No. Everything happens inside your browser using the built-in image decoder and canvas. The site has no backend and no upload endpoint."),
        ],
    },
    {
        "slug": "jpg-to-png",
        "source": "jpeg",
        "target": "png",
        "title": "JPG to PNG Converter - Free Online Tool (No Upload)",
        "description": (
            "Convert JPG to PNG online for free. Get a lossless PNG copy for editing, transparency work "
            "or upload requirements. Runs in your browser — images are never uploaded."
        ),
        "h1": "JPG to PNG Converter",
        "lede": (
            "Convert JPG images to lossless PNG in your browser. Free, unlimited, no sign-up, and your "
            "files never leave your device."
        ),
        "card": "Get a lossless PNG copy of a JPG for editing or transparency work.",
        "about_h2": "What changes when you convert JPG to PNG",
        "about": [
            "JPEG stores an approximation of an image. Its encoder discards detail the eye is unlikely to "
            "miss, which is why photographs compress so well — and why every re-save degrades the picture a "
            "little further.",
            "PNG stores the image exactly. Converting a JPG to PNG does not repair anything that JPEG already "
            "threw away, but it does stop the bleeding: from that point on you can crop, retouch and re-save "
            "as many times as you like without adding a single new artefact. That is the main reason to make "
            "the switch.",
        ],
        "why_h2": "Why convert JPG to PNG?",
        "why": [
            ("Editing without generation loss.", "Every JPEG save re-compresses the whole image. Work in PNG and repeated saves cost you nothing."),
            ("You need transparency.", "JPEG cannot store an alpha channel at all. Convert to PNG first, then erase the background in your editor."),
            ("Upload requirements.", "Some form builders, print templates and app stores specify PNG for logos, icons and screenshots."),
            ("Sharper overlays.", "Text, watermarks and UI elements pasted onto a JPEG pick up ringing artefacts; the same work saved as PNG stays crisp."),
            ("Documents and presentations.", "PNG avoids the visible block artefacts that show up when a JPEG is scaled inside a slide or PDF."),
        ],
        "notes_h2": "Honest expectations",
        "notes": [
            "<strong>Converting to PNG does not improve the image.</strong> Compression artefacts already "
            "present in the JPEG — blockiness in flat areas, halos along high-contrast edges — are copied "
            "faithfully into the PNG. Nothing can recover the original detail, because it was discarded when "
            "the JPEG was first written.",
            "<strong>Expect a much larger file.</strong> A 500 KB JPEG photograph commonly becomes a 3–5 MB "
            "PNG. That is the cost of lossless storage on photographic content, not a fault in the "
            "conversion. Convert for editing and archiving, not to save space.",
            "The PNG produced here is fully opaque, because the JPEG it came from had no transparency to "
            "carry over. You can erase areas to transparent afterwards in any image editor.",
        ],
        "faqs": [
            ("How do I convert JPG to PNG?", "Drop your JPG or JPEG files onto the area at the top of this page, press Convert to PNG, then download the results individually or as a ZIP."),
            ("Does converting JPG to PNG improve quality?", "No. The conversion is lossless, but it cannot restore detail the JPEG encoder already discarded. Existing artefacts are preserved exactly. What it does give you is a format that will not degrade further with each save."),
            ("Why is the PNG so much bigger than the JPG?", "PNG is lossless, so it stores every pixel of a noisy photograph exactly, while JPEG stores a compact approximation. Growth of five to ten times is normal for photographic content."),
            ("Does the PNG have a transparent background?", "No. JPEG has no alpha channel, so there is no transparency to carry across and the result is fully opaque. You can erase parts to transparent afterwards in an image editor."),
            ("Can I convert multiple JPG files at once?", "Yes. Add as many as you like, convert in one pass, and use Download all as ZIP for a single archive."),
            ("Does it work with .jpeg and .jfif files?", "Yes. Those are the same format with different extensions, and all of them are accepted."),
            ("Are my photos uploaded to a server?", "No. Conversion happens entirely in your browser. The site is static, with no backend and no upload endpoint, so your images never leave your device."),
        ],
    },
    {
        "slug": "png-to-webp",
        "source": "png",
        "target": "webp",
        "title": "PNG to WebP Converter - Free Online Tool (No Upload)",
        "description": (
            "Convert PNG to WebP online for free and cut image weight while keeping transparency. "
            "Adjustable quality and batch conversion, entirely inside your browser."
        ),
        "h1": "PNG to WebP Converter",
        "lede": (
            "Convert PNG images to WebP to make your pages faster, with transparency intact. "
            "Free, unlimited, and nothing is uploaded."
        ),
        "card": "Compress PNG images into smaller WebP files while keeping transparency.",
        "about_h2": "Why WebP replaced PNG on the web",
        "about": [
            "WebP was designed for exactly this job: delivering images over a network. On the same "
            "photograph it is usually 25–35% smaller than JPEG, and against PNG the gap is far wider still, "
            "because WebP can compress with loss where PNG never can.",
            "Crucially, it does this without giving up an alpha channel. Before WebP, keeping transparency "
            "meant accepting PNG's file sizes. Now every browser in current use — Chrome, Firefox, Safari, "
            "Edge, and their mobile versions — renders WebP natively, so that trade-off is gone.",
        ],
        "why_h2": "Why convert PNG to WebP?",
        "why": [
            ("Core Web Vitals.", "Images are usually the heaviest thing on a page. Cutting their weight directly improves Largest Contentful Paint, which Google uses as a ranking signal."),
            ("Transparency kept.", "Unlike JPEG, WebP has a full alpha channel, so logos and cut-outs survive the conversion intact."),
            ("Lower bandwidth bills.", "On an image-heavy site or CDN, a large reduction in bytes served shows up directly on the invoice."),
            ("Faster on mobile networks.", "Smaller images matter most on the slow, high-latency connections where visitors are quickest to leave."),
            ("Same visual result.", "At sensible quality settings the difference from the PNG original is invisible at normal viewing size."),
        ],
        "notes_h2": "Choosing a quality level",
        "notes": [
            "The quality slider controls lossy WebP encoding. 85% is a sound default for photographs and "
            "complex graphics. For logos, icons, screenshots of text and line art, push it to 95–100%, where "
            "WebP still beats PNG on size but keeps edges perfectly crisp — lossy compression is unkind to "
            "sharp boundaries.",
            "<strong>Transparency is preserved</strong> throughout, so there is no background colour to "
            "choose. Semi-transparent pixels come through with their alpha values intact.",
            "Keep your PNG originals. WebP is a delivery format; if you will edit the image again later, "
            "edit the lossless source and re-export.",
        ],
        "faqs": [
            ("How do I convert PNG to WebP?", "Add your PNG files to the drop area, set a quality level if you want something other than 85%, press Convert to WebP, and download the results."),
            ("Does WebP keep PNG transparency?", "Yes. WebP supports a full alpha channel, so transparent and semi-transparent areas are preserved exactly as they were in the PNG."),
            ("How much smaller will the WebP be?", "For photographs and rich graphics, commonly 60–90% smaller than the PNG. For simple flat-colour icons the saving is more modest, since PNG is already efficient on that kind of content."),
            ("Do all browsers support WebP?", "Yes. Every browser in current use renders WebP, including Safari since version 14 and all current mobile browsers. Support has not been a practical concern for several years."),
            ("Is WebP conversion lossy or lossless?", "This tool writes lossy WebP, controlled by the quality slider. Set it to 100% for the highest fidelity, which is still typically much smaller than the source PNG."),
            ("Can I convert a whole folder of PNGs at once?", "You can select as many files as you like in one go and convert them in a single pass, then download them together as a ZIP archive."),
            ("Are my images uploaded to a server?", "No. The encoding runs on your own device using your browser's canvas. This site has no backend and no upload endpoint."),
        ],
    },
    {
        "slug": "jpg-to-webp",
        "source": "jpeg",
        "target": "webp",
        "title": "JPG to WebP Converter - Free Online Tool (No Upload)",
        "description": (
            "Convert JPG to WebP online for free and cut photo file sizes by around a third. "
            "Adjustable quality, batch conversion, and nothing is ever uploaded."
        ),
        "h1": "JPG to WebP Converter",
        "lede": (
            "Convert JPG photos to WebP and cut their size without a visible difference. "
            "Free, unlimited, and everything runs in your browser."
        ),
        "card": "Convert JPG photos to WebP and cut page weight by roughly a third.",
        "about_h2": "WebP versus JPEG for photographs",
        "about": [
            "JPEG's compression dates from 1992 and has aged remarkably well, but WebP's encoder is thirty "
            "years newer. On the same photograph at matched visual quality, WebP files typically come out "
            "25–35% smaller — the single easiest saving available on most image-heavy websites.",
            "The catch is that both are lossy formats, so converting one to the other means encoding "
            "already-encoded data. Done at a sensible quality that is invisible; done carelessly it stacks "
            "artefacts on top of artefacts.",
        ],
        "why_h2": "Why convert JPG to WebP?",
        "why": [
            ("Page speed.", "Photographs dominate the weight of most pages, and a third off every one of them is a substantial improvement to load time."),
            ("Better ranking signals.", "Faster image delivery improves Largest Contentful Paint, which feeds directly into Google's page experience signals."),
            ("Lower bandwidth costs.", "Serving fewer bytes from a CDN or host reduces the bill on high-traffic sites."),
            ("Modern CMS pipelines.", "WordPress, Shopify and most static site generators now prefer WebP, and many will serve it automatically if you supply it."),
            ("Same picture, less data.", "At the default quality, side-by-side comparison at normal viewing size shows no visible difference."),
        ],
        "notes_h2": "Avoiding double compression",
        "notes": [
            "Because your JPG is already lossy, re-encoding to lossy WebP is a second round of compression. "
            "The practical rule: encode WebP at a quality at least as high as the JPEG's, and never chase "
            "extra savings by dropping the slider low. 85% is a safe default here; go to 90–95% for images "
            "with fine texture, text overlays or hard edges.",
            "Where possible, generate WebP from the original camera file or lossless master rather than from "
            "a JPEG. If the JPG is all you have, converting at high quality is still worthwhile — just "
            "keep the JPG as your archive copy.",
            "The result is fully opaque, since JPEG carries no transparency to preserve.",
        ],
        "faqs": [
            ("How do I convert JPG to WebP?", "Drop your JPG files onto the area at the top of this page, choose a quality level if you want to, press Convert to WebP, and download the results."),
            ("How much smaller is WebP than JPG?", "Typically 25–35% smaller at equivalent visual quality, though the exact figure depends on the image. Photographs with smooth gradients benefit most."),
            ("Will converting JPG to WebP reduce quality?", "Slightly, because it is a second lossy encode. At 85% and above the difference is not visible at normal viewing size. Keep the quality high and keep your JPG originals."),
            ("Do all browsers support WebP?", "Yes. Chrome, Firefox, Safari 14 and later, Edge and all current mobile browsers display WebP natively."),
            ("Should I convert JPG to WebP or AVIF?", "AVIF compresses better still, but encodes slowly and has patchier tooling support. WebP is the pragmatic choice for most sites today, and this tool produces it instantly in your browser."),
            ("Can I convert lots of photos at once?", "Yes. Add as many JPG files as you like, convert them in one pass, and download them together as a ZIP archive."),
            ("Are my photos uploaded anywhere?", "No. Encoding happens on your own device through your browser's canvas. The site is static, with no backend and no upload endpoint."),
        ],
    },
]

# --------------------------------------------------------------------------
# Shared FAQ entries appended to every tool page
# --------------------------------------------------------------------------
COMMON_FAQS = [
    ("Is there a limit on image size?", "There is no fixed file-size limit, but conversion is bounded by your device's memory and your browser's maximum canvas size. Images wider or taller than 16,384 pixels may fail — mobile Safari is the strictest here. The tool tells you when an image exceeds what your browser can handle."),
    ("Can I use this converter on mobile?", "Yes. The page is responsive and works in mobile Chrome, Safari, Firefox and Edge. Very large images may fail on phones because of tighter memory limits."),
]
