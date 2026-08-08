/**
 * UI layer shared by every converter page.
 *
 * The page declares which formats it handles in a JSON block:
 *   <script type="application/json" id="tool-config">{"source":"webp","target":"png"}</script>
 * Everything else — labels, accepted types, quality controls — follows from that,
 * so all tool pages run the same tested code path.
 */

import {
  ConversionError,
  SOURCE_FORMATS,
  TARGET_FORMATS,
  canEncode,
  convertImage,
  formatBytes,
  makeUniqueName,
  retargetFilename,
  sizeDelta,
  validateFile,
} from './converter.js';
import { createZip } from './zip.js';

const configNode = document.getElementById('tool-config');
const config = configNode ? JSON.parse(configNode.textContent) : { source: 'webp', target: 'png' };
const SOURCE = SOURCE_FORMATS[config.source];
const TARGET = TARGET_FORMATS[config.target];
const DEFAULT_QUALITY = config.target === 'jpeg' ? 0.92 : 0.85;

const el = {
  dropzone: document.getElementById('dropzone'),
  input: document.getElementById('file-input'),
  list: document.getElementById('file-list'),
  status: document.getElementById('status'),
  progress: document.getElementById('progress'),
  progressBar: document.getElementById('progress-bar'),
  options: document.getElementById('options'),
  quality: document.getElementById('quality'),
  qualityValue: document.getElementById('quality-value'),
  background: document.getElementById('background'),
  toolbar: document.getElementById('toolbar'),
  convertBtn: document.getElementById('convert-btn'),
  downloadAllBtn: document.getElementById('download-all-btn'),
  clearBtn: document.getElementById('clear-btn'),
};

/** @type {Array<Item>} */
const items = [];
let nextId = 1;
let isConverting = false;

/**
 * @typedef {Object} Item
 * @property {number} id
 * @property {File} file
 * @property {string} previewUrl   object URL for the on-screen thumbnail
 * @property {string} outputUrl    object URL for the converted file ('' until converted)
 * @property {Blob|null} outputBlob
 * @property {string} outputName
 * @property {number} width
 * @property {number} height
 * @property {'pending'|'converting'|'done'|'error'} status
 * @property {string} message
 * @property {HTMLLIElement|null} node
 * @property {Object|null} refs
 */

/* ------------------------------------------------------------------ *
 * Status reporting
 * ------------------------------------------------------------------ */

function setStatus(text, tone = '') {
  el.status.textContent = text;
  el.status.className = tone ? `status is-${tone}` : 'status';
}

function setProgress(done, total) {
  if (!total) {
    el.progress.hidden = true;
    return;
  }
  const percent = Math.round((done / total) * 100);
  el.progress.hidden = false;
  el.progressBar.style.width = `${percent}%`;
  el.progressBar.setAttribute('aria-valuenow', String(percent));
}

/* ------------------------------------------------------------------ *
 * Adding files
 * ------------------------------------------------------------------ */

function isDuplicate(file) {
  return items.some(
    (item) =>
      item.file.name === file.name &&
      item.file.size === file.size &&
      item.file.lastModified === file.lastModified
  );
}

async function addFiles(fileList) {
  const incoming = Array.from(fileList || []);
  if (incoming.length === 0) return;

  let added = 0;
  let rejected = 0;
  let duplicates = 0;

  for (const file of incoming) {
    if (isDuplicate(file)) {
      duplicates++;
      continue;
    }

    const check = await validateFile(file, SOURCE);
    const item = createItem(file);

    if (!check.ok) {
      item.status = 'error';
      item.message = check.reason;
      rejected++;
    } else {
      added++;
    }

    items.push(item);
    renderItem(item);
    if (check.ok) loadPreview(item);
  }

  syncToolbar();

  const parts = [];
  if (added) parts.push(`${added} ${added === 1 ? 'image' : 'images'} ready to convert.`);
  if (rejected) parts.push(`${rejected} ${rejected === 1 ? 'file was' : 'files were'} rejected.`);
  if (duplicates) parts.push(`${duplicates} duplicate ${duplicates === 1 ? 'file' : 'files'} skipped.`);
  setStatus(parts.join(' '), rejected && !added ? 'error' : '');
}

function createItem(file) {
  return {
    id: nextId++,
    file,
    previewUrl: URL.createObjectURL(file),
    outputUrl: '',
    outputBlob: null,
    outputName: retargetFilename(file.name, TARGET.extension),
    width: 0,
    height: 0,
    status: 'pending',
    message: '',
    node: null,
    refs: null,
  };
}

/**
 * The thumbnail doubles as a decode test: if the browser cannot render the
 * image here, it will not be able to convert it either, so we fail early with
 * a clear message instead of at conversion time.
 */
function loadPreview(item) {
  const img = item.refs.image;
  img.addEventListener(
    'load',
    () => {
      item.width = img.naturalWidth;
      item.height = img.naturalHeight;
      updateItem(item);
    },
    { once: true }
  );
  img.addEventListener(
    'error',
    () => {
      item.status = 'error';
      item.message = 'This image could not be read. It may be corrupted.';
      updateItem(item);
      syncToolbar();
    },
    { once: true }
  );
  img.src = item.previewUrl;
  img.alt = `Preview of ${item.file.name}`;
}

/* ------------------------------------------------------------------ *
 * Rendering
 * ------------------------------------------------------------------ */

function makeEl(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text != null) node.textContent = text; // textContent, never innerHTML: filenames are untrusted
  return node;
}

const TRASH_ICON =
  '<svg width="16" height="16" viewBox="0 0 24 24" aria-hidden="true" focusable="false">' +
  '<path d="M4 7h16M10 7V5.5A1.5 1.5 0 0 1 11.5 4h1A1.5 1.5 0 0 1 14 5.5V7m-7 0 .8 12.1A1.9 1.9 0 0 0 9.7 21h4.6a1.9 1.9 0 0 0 1.9-1.9L17 7" ' +
  'fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/></svg>';

// Copying an image to the clipboard is only reliably supported for PNG.
const CAN_COPY =
  TARGET.mimeType === 'image/png' &&
  typeof ClipboardItem === 'function' &&
  Boolean(navigator.clipboard?.write);

function renderItem(item) {
  const li = makeEl('li', 'file-item');

  const thumb = makeEl('div', 'thumb');
  const image = makeEl('img');
  image.decoding = 'async';
  image.loading = 'lazy';
  image.alt = '';
  // Shown instead of the preview when the file could not be read at all.
  const fallback = makeEl('span', 'thumb-fallback', 'N/A');
  fallback.hidden = true;
  thumb.append(image, fallback);

  const meta = makeEl('div', 'file-meta');
  const name = makeEl('p', 'file-name', item.file.name);
  name.title = item.file.name;
  const sub = makeEl('p', 'file-sub');
  meta.append(name, sub);

  const actions = makeEl('div', 'file-actions');

  const download = makeEl('a', 'btn btn-secondary btn-sm', `Download ${TARGET.label}`);
  download.hidden = true;

  const copy = makeEl('button', 'btn btn-ghost btn-sm', 'Copy');
  copy.type = 'button';
  copy.hidden = true;
  if (CAN_COPY) copy.addEventListener('click', () => copyToClipboard(item, copy));

  const remove = makeEl('button', 'icon-btn');
  remove.type = 'button';
  remove.innerHTML = TRASH_ICON; // static markup, no user data
  remove.setAttribute('aria-label', `Remove ${item.file.name}`);
  remove.addEventListener('click', () => removeItem(item.id));

  actions.append(download, copy, remove);
  li.append(thumb, meta, actions);

  item.node = li;
  item.refs = { image, fallback, sub, download, copy };
  el.list.append(li);
  updateItem(item);
}

function updateItem(item) {
  const { sub, download, copy, image, fallback } = item.refs;
  sub.textContent = '';

  const unreadable = item.status === 'error' && !item.width;
  image.hidden = unreadable;
  fallback.hidden = !unreadable;

  const facts = [];
  if (item.width && item.height) facts.push(`${item.width} × ${item.height} px`);
  facts.push(formatBytes(item.file.size));

  facts.forEach((fact, index) => {
    if (index > 0) sub.append(makeEl('span', 'sep', '·'));
    sub.append(document.createTextNode(fact));
  });

  const state = makeEl('span', 'file-state');
  switch (item.status) {
    case 'pending':
      state.textContent = 'Ready';
      break;
    case 'converting':
      state.textContent = 'Converting…';
      break;
    case 'done': {
      state.className = 'file-state is-done';
      const delta = sizeDelta(item.file.size, item.outputBlob.size);
      state.textContent = `${TARGET.label} · ${formatBytes(item.outputBlob.size)}${delta ? ` (${delta})` : ''}`;
      break;
    }
    case 'error':
      state.className = 'file-state is-error';
      state.textContent = item.message;
      break;
  }
  sub.append(makeEl('span', 'sep', '·'), state);

  item.node.classList.toggle('is-error', item.status === 'error');

  if (item.status === 'done') {
    download.hidden = false;
    download.href = item.outputUrl;
    download.download = item.outputName;
    download.setAttribute('aria-label', `Download ${item.outputName}`);
    copy.hidden = !CAN_COPY;
    if (CAN_COPY) copy.setAttribute('aria-label', `Copy ${item.outputName} to clipboard`);
  } else {
    download.hidden = true;
    copy.hidden = true;
  }
}

async function copyToClipboard(item, button) {
  if (!item.outputBlob) return;
  const original = button.textContent;
  try {
    await navigator.clipboard.write([new ClipboardItem({ [TARGET.mimeType]: item.outputBlob })]);
    button.textContent = 'Copied';
    setStatus(`${item.outputName} copied to the clipboard.`, 'done');
  } catch (error) {
    console.error('Clipboard write failed:', error);
    button.textContent = 'Failed';
    setStatus('Your browser blocked the clipboard. Use Download instead.', 'error');
  }
  setTimeout(() => {
    button.textContent = original;
  }, 2000);
}

function removeItem(id) {
  const index = items.findIndex((item) => item.id === id);
  if (index === -1) return;
  const [item] = items.splice(index, 1);
  releaseItem(item);
  item.node.remove();
  syncToolbar();
  setStatus(items.length ? `Removed ${item.file.name}.` : 'All files removed.');
}

function releaseItem(item) {
  if (item.previewUrl) URL.revokeObjectURL(item.previewUrl);
  if (item.outputUrl) URL.revokeObjectURL(item.outputUrl);
  item.previewUrl = '';
  item.outputUrl = '';
  item.outputBlob = null;
}

function clearAll() {
  items.forEach(releaseItem);
  items.length = 0;
  el.list.replaceChildren();
  el.input.value = '';
  syncToolbar();
  setProgress(0, 0);
  setStatus(`Cleared. Add ${SOURCE.label} files to start again.`);
}

/** Enables/disables the toolbar to match what is actually possible right now. */
function syncToolbar() {
  const convertible = items.filter((item) => item.status === 'pending').length;
  const converted = items.filter((item) => item.status === 'done').length;

  el.toolbar.hidden = items.length === 0;
  if (el.options) el.options.hidden = items.length === 0;
  el.convertBtn.disabled = isConverting || convertible === 0;
  el.convertBtn.textContent =
    convertible > 1 ? `Convert ${convertible} images to ${TARGET.label}` : `Convert to ${TARGET.label}`;
  el.clearBtn.disabled = isConverting;
  el.downloadAllBtn.hidden = converted < 2;
  el.downloadAllBtn.disabled = isConverting;
}

/* ------------------------------------------------------------------ *
 * Conversion
 * ------------------------------------------------------------------ */

/** Hands control back to the browser so the UI can paint between images. */
const yieldToUi = () => new Promise((resolve) => setTimeout(resolve, 0));

function currentOptions() {
  return {
    target: TARGET,
    quality: el.quality ? Number(el.quality.value) / 100 : DEFAULT_QUALITY,
    background: el.background ? el.background.value : '#ffffff',
  };
}

async function convertAll() {
  const queue = items.filter((item) => item.status === 'pending');
  if (queue.length === 0 || isConverting) return;

  if (!(await canEncode(TARGET.mimeType))) {
    setStatus(`Your browser cannot create ${TARGET.label} files. Try Chrome, Edge or Firefox.`, 'error');
    return;
  }

  isConverting = true;
  syncToolbar();
  el.list.setAttribute('aria-busy', 'true');

  const options = currentOptions();
  let succeeded = 0;
  let failed = 0;

  for (let i = 0; i < queue.length; i++) {
    const item = queue[i];
    item.status = 'converting';
    updateItem(item);
    setStatus(`Converting ${i + 1} of ${queue.length}: ${item.file.name}`);
    setProgress(i, queue.length);
    await yieldToUi();

    try {
      const result = await convertImage(item.file, options);
      item.outputBlob = result.blob;
      item.outputUrl = URL.createObjectURL(result.blob);
      item.width = result.width;
      item.height = result.height;
      item.status = 'done';
      succeeded++;
    } catch (error) {
      item.status = 'error';
      item.message =
        error instanceof ConversionError
          ? error.message
          : 'Conversion failed. The file may be corrupted or too large for this device.';
      failed++;
      if (!(error instanceof ConversionError)) console.error('Conversion failed:', error);
    }
    updateItem(item);
  }

  setProgress(queue.length, queue.length);
  el.list.removeAttribute('aria-busy');
  isConverting = false;
  syncToolbar();

  if (failed === 0) {
    setStatus(
      succeeded === 1
        ? `Done. Your ${TARGET.label} is ready to download.`
        : `Done. ${succeeded} ${TARGET.label} files are ready to download.`,
      'done'
    );
  } else if (succeeded === 0) {
    setStatus(`Conversion failed for ${failed === 1 ? 'the image' : `all ${failed} images`}. See the details in the list.`, 'error');
  } else {
    setStatus(`${succeeded} converted, ${failed} failed. See the details in the list.`, 'error');
  }
}

/* ------------------------------------------------------------------ *
 * Downloads
 * ------------------------------------------------------------------ */

function triggerDownload(blob, filename) {
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.append(link);
  link.click();
  link.remove();
  // Revoke once the browser has had a chance to start the download.
  setTimeout(() => URL.revokeObjectURL(url), 60_000);
}

async function downloadAll() {
  const converted = items.filter((item) => item.status === 'done');
  if (converted.length === 0) return;

  el.downloadAllBtn.disabled = true;
  setStatus('Building ZIP archive…');

  try {
    const taken = new Set();
    const zip = await createZip(
      converted.map((item) => ({ name: makeUniqueName(item.outputName, taken), blob: item.outputBlob }))
    );
    triggerDownload(zip, `converted-${TARGET.extension}-images.zip`);
    setStatus(`ZIP archive with ${converted.length} ${TARGET.label} files downloaded.`, 'done');
  } catch (error) {
    console.error('ZIP creation failed:', error);
    setStatus(
      error instanceof Error && error.message
        ? error.message
        : 'The ZIP archive could not be created. Download the images individually instead.',
      'error'
    );
  } finally {
    el.downloadAllBtn.disabled = false;
  }
}

/* ------------------------------------------------------------------ *
 * Events
 * ------------------------------------------------------------------ */

el.input.accept = SOURCE.accept;

el.input.addEventListener('change', () => {
  addFiles(el.input.files);
  // Reset so re-selecting the same file still fires a change event.
  el.input.value = '';
});

el.convertBtn.addEventListener('click', convertAll);
el.downloadAllBtn.addEventListener('click', downloadAll);
el.clearBtn.addEventListener('click', clearAll);

if (el.quality) {
  el.quality.value = String(Math.round(DEFAULT_QUALITY * 100));
  const showQuality = () => {
    el.qualityValue.textContent = `${el.quality.value}%`;
  };
  el.quality.addEventListener('input', showQuality);
  showQuality();
}

['dragenter', 'dragover'].forEach((type) => {
  el.dropzone.addEventListener(type, (event) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'copy';
    el.dropzone.classList.add('is-dragover');
  });
});

['dragleave', 'dragend'].forEach((type) => {
  el.dropzone.addEventListener(type, (event) => {
    // Ignore drags moving between child elements of the drop zone.
    if (event.relatedTarget && el.dropzone.contains(event.relatedTarget)) return;
    el.dropzone.classList.remove('is-dragover');
  });
});

el.dropzone.addEventListener('drop', (event) => {
  event.preventDefault();
  el.dropzone.classList.remove('is-dragover');
  addFiles(event.dataTransfer.files);
});

// A file dropped outside the drop zone would otherwise navigate away from the
// page and silently discard whatever the user had queued up.
['dragover', 'drop'].forEach((type) => {
  window.addEventListener(type, (event) => {
    if (!el.dropzone.contains(event.target)) event.preventDefault();
  });
});

window.addEventListener('beforeunload', () => items.forEach(releaseItem));

// Warn once, up front, if this browser cannot write the target format at all.
canEncode(TARGET.mimeType).then((supported) => {
  if (!supported) {
    setStatus(`Your browser cannot create ${TARGET.label} files. Try Chrome, Edge or Firefox.`, 'error');
  }
});

syncToolbar();
