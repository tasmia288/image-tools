/**
 * UI layer for the WebP -> PNG converter.
 *
 * Owns the file list, the drop zone, progress reporting and downloads.
 * All image work is delegated to converter.js; all archiving to zip.js.
 */

import {
  ConversionError,
  convertWebpToPng,
  formatBytes,
  makeUniqueName,
  toPngFilename,
  validateWebpFile,
} from './converter.js';
import { createZip } from './zip.js';

const el = {
  dropzone: document.getElementById('dropzone'),
  input: document.getElementById('file-input'),
  list: document.getElementById('file-list'),
  status: document.getElementById('status'),
  progress: document.getElementById('progress'),
  progressBar: document.getElementById('progress-bar'),
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
 * @property {string} pngUrl       object URL for the converted PNG ('' until converted)
 * @property {Blob|null} pngBlob
 * @property {string} pngName
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

    const check = await validateWebpFile(file);
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
    pngUrl: '',
    pngBlob: null,
    pngName: toPngFilename(file.name),
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
 * WebP here, it will not be able to convert it either, so we fail early with
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

  const download = makeEl('a', 'btn btn-secondary btn-sm', 'Download PNG');
  download.hidden = true;

  const remove = makeEl('button', 'icon-btn');
  remove.type = 'button';
  remove.innerHTML = TRASH_ICON; // static markup, no user data
  remove.setAttribute('aria-label', `Remove ${item.file.name}`);
  remove.addEventListener('click', () => removeItem(item.id));

  actions.append(download, remove);
  li.append(thumb, meta, actions);

  item.node = li;
  item.refs = { image, fallback, sub, download };
  el.list.append(li);
  updateItem(item);
}

function updateItem(item) {
  const { sub, download, image, fallback } = item.refs;
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
      state.className = 'file-state';
      break;
    case 'converting':
      state.textContent = 'Converting…';
      break;
    case 'done':
      state.className = 'file-state is-done';
      state.textContent = `PNG · ${formatBytes(item.pngBlob.size)}`;
      break;
    case 'error':
      state.className = 'file-state is-error';
      state.textContent = item.message;
      break;
  }
  sub.append(makeEl('span', 'sep', '·'), state);

  item.node.classList.toggle('is-error', item.status === 'error');

  if (item.status === 'done') {
    download.hidden = false;
    download.href = item.pngUrl;
    download.download = item.pngName;
    download.setAttribute('aria-label', `Download ${item.pngName}`);
  } else {
    download.hidden = true;
  }
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
  if (item.pngUrl) URL.revokeObjectURL(item.pngUrl);
  item.previewUrl = '';
  item.pngUrl = '';
  item.pngBlob = null;
}

function clearAll() {
  items.forEach(releaseItem);
  items.length = 0;
  el.list.replaceChildren();
  el.input.value = '';
  syncToolbar();
  setProgress(0, 0);
  setStatus('Cleared. Add WebP files to start again.');
}

/** Enables/disables the toolbar to match what is actually possible right now. */
function syncToolbar() {
  const convertible = items.filter((item) => item.status === 'pending').length;
  const converted = items.filter((item) => item.status === 'done').length;

  el.toolbar.hidden = items.length === 0;
  el.convertBtn.disabled = isConverting || convertible === 0;
  el.convertBtn.textContent =
    convertible > 1 ? `Convert ${convertible} images to PNG` : 'Convert to PNG';
  el.clearBtn.disabled = isConverting;
  el.downloadAllBtn.hidden = converted < 2;
  el.downloadAllBtn.disabled = isConverting;
}

/* ------------------------------------------------------------------ *
 * Conversion
 * ------------------------------------------------------------------ */

/** Hands control back to the browser so the UI can paint between images. */
const yieldToUi = () => new Promise((resolve) => setTimeout(resolve, 0));

async function convertAll() {
  const queue = items.filter((item) => item.status === 'pending');
  if (queue.length === 0 || isConverting) return;

  isConverting = true;
  syncToolbar();
  el.list.setAttribute('aria-busy', 'true');

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
      const result = await convertWebpToPng(item.file);
      item.pngBlob = result.blob;
      item.pngUrl = URL.createObjectURL(result.blob);
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
        ? 'Done. Your PNG is ready to download.'
        : `Done. ${succeeded} PNG files are ready to download.`,
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
      converted.map((item) => ({ name: makeUniqueName(item.pngName, taken), blob: item.pngBlob }))
    );
    triggerDownload(zip, 'converted-png-images.zip');
    setStatus(`ZIP archive with ${converted.length} PNG files downloaded.`, 'done');
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

el.input.addEventListener('change', () => {
  addFiles(el.input.files);
  // Reset so re-selecting the same file still fires a change event.
  el.input.value = '';
});

el.convertBtn.addEventListener('click', convertAll);
el.downloadAllBtn.addEventListener('click', downloadAll);
el.clearBtn.addEventListener('click', clearAll);

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

const yearEl = document.getElementById('year');
if (yearEl) yearEl.textContent = String(new Date().getFullYear());

syncToolbar();
