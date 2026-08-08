/**
 * WebP -> PNG conversion, using only browser-native APIs.
 *
 * Nothing here performs a network request: files are read from the user's disk
 * by the browser, decoded by the browser's image decoder, and re-encoded to PNG
 * through a canvas. There is no upload path anywhere in this codebase.
 */

/** Widest dimension any mainstream browser will accept for a canvas. */
const MAX_CANVAS_SIDE = 16384;

/** Errors we raise deliberately, so the UI can show them verbatim. */
export class ConversionError extends Error {}

/* ------------------------------------------------------------------ *
 * Validation
 * ------------------------------------------------------------------ */

/** Cheap first pass: does this even claim to be a WebP? */
export function looksLikeWebp(file) {
  return file.type === 'image/webp' || /\.webp$/i.test(file.name);
}

/**
 * Authoritative check: a WebP file is a RIFF container whose form type is
 * "WEBP", i.e. bytes 0-3 are "RIFF" and bytes 8-11 are "WEBP". Reading 12 bytes
 * catches files that were merely renamed to .webp.
 */
export async function hasWebpSignature(file) {
  if (file.size < 12) return false;
  const header = new Uint8Array(await file.slice(0, 12).arrayBuffer());
  const ascii = (start, end) => String.fromCharCode(...header.slice(start, end));
  return ascii(0, 4) === 'RIFF' && ascii(8, 12) === 'WEBP';
}

/**
 * Runs both checks and returns a human-readable reason on failure.
 * @returns {Promise<{ok: true} | {ok: false, reason: string}>}
 */
export async function validateWebpFile(file) {
  if (file.size === 0) {
    return { ok: false, reason: 'This file is empty.' };
  }
  if (!looksLikeWebp(file)) {
    const kind = file.type ? file.type.replace(/^image\//, '').toUpperCase() : 'unknown';
    return { ok: false, reason: `Not a WebP file (detected ${kind}). This tool only converts .webp images.` };
  }
  if (!(await hasWebpSignature(file))) {
    return { ok: false, reason: 'This file is named .webp but its contents are not a valid WebP image.' };
  }
  return { ok: true };
}

/* ------------------------------------------------------------------ *
 * Decoding
 * ------------------------------------------------------------------ */

/**
 * Decodes a file to something drawable. `createImageBitmap` is preferred: it
 * decodes off the main thread, so the UI keeps responding on large images.
 * Older Safari falls back to an <img> element.
 * @returns {Promise<ImageBitmap|HTMLImageElement>}
 */
async function decodeImage(file) {
  if (typeof createImageBitmap === 'function') {
    try {
      return await createImageBitmap(file);
    } catch {
      /* Fall through to the <img> path rather than failing outright. */
    }
  }

  const url = URL.createObjectURL(file);
  try {
    return await new Promise((resolve, reject) => {
      const img = new Image();
      img.decoding = 'async';
      img.onload = () => resolve(img);
      img.onerror = () => reject(new ConversionError('The image could not be decoded. It may be corrupted, or your browser may not support this WebP variant.'));
      img.src = url;
    });
  } finally {
    URL.revokeObjectURL(url);
  }
}

/** Reads intrinsic size from either decode result. */
function sizeOf(source) {
  return {
    width: source.width || source.naturalWidth || 0,
    height: source.height || source.naturalHeight || 0,
  };
}

/* ------------------------------------------------------------------ *
 * Encoding
 * ------------------------------------------------------------------ */

/** Draws the decoded image and encodes it as PNG. */
async function encodePng(source, width, height) {
  const useOffscreen =
    typeof OffscreenCanvas === 'function' &&
    typeof OffscreenCanvas.prototype.convertToBlob === 'function';

  const canvas = useOffscreen
    ? new OffscreenCanvas(width, height)
    : Object.assign(document.createElement('canvas'), { width, height });

  // `alpha: true` (the default) matters: WebP transparency must survive.
  const ctx = canvas.getContext('2d');
  if (!ctx) throw new ConversionError('Your browser could not create a drawing canvas for this image.');
  ctx.drawImage(source, 0, 0, width, height);

  const blob = useOffscreen
    ? await canvas.convertToBlob({ type: 'image/png' })
    : await new Promise((resolve) => canvas.toBlob(resolve, 'image/png'));

  if (!blob || blob.size === 0) {
    throw new ConversionError('Encoding failed, most likely because the image is too large for this device.');
  }
  return blob;
}

/**
 * Converts one validated WebP file to a PNG blob.
 * @param {File} file
 * @returns {Promise<{blob: Blob, width: number, height: number}>}
 */
export async function convertWebpToPng(file) {
  const source = await decodeImage(file);
  try {
    const { width, height } = sizeOf(source);
    if (!width || !height) {
      throw new ConversionError('The image has no readable dimensions and cannot be converted.');
    }
    if (width > MAX_CANVAS_SIDE || height > MAX_CANVAS_SIDE) {
      throw new ConversionError(
        `This image is ${width}×${height} pixels. Browsers cannot draw a canvas larger than ${MAX_CANVAS_SIDE} pixels on a side.`
      );
    }
    const blob = await encodePng(source, width, height);
    return { blob, width, height };
  } finally {
    // ImageBitmaps hold decoded pixels; release them as soon as we are done.
    if (typeof source.close === 'function') source.close();
  }
}

/* ------------------------------------------------------------------ *
 * Small helpers shared with the UI
 * ------------------------------------------------------------------ */

/** "photo.webp" -> "photo.png"; also strips any directory component. */
export function toPngFilename(name) {
  const base = name.split(/[\\/]/).pop() || 'image';
  return `${base.replace(/\.webp$/i, '') || 'image'}.png`;
}

/** Ensures every name in a batch is unique, so a ZIP never has collisions. */
export function makeUniqueName(name, taken) {
  if (!taken.has(name)) {
    taken.add(name);
    return name;
  }
  const dot = name.lastIndexOf('.');
  const stem = dot === -1 ? name : name.slice(0, dot);
  const ext = dot === -1 ? '' : name.slice(dot);
  let n = 2;
  let candidate = `${stem}-${n}${ext}`;
  while (taken.has(candidate)) candidate = `${stem}-${++n}${ext}`;
  taken.add(candidate);
  return candidate;
}

export function formatBytes(bytes) {
  if (!Number.isFinite(bytes) || bytes < 0) return '—';
  if (bytes < 1024) return `${bytes} B`;
  const units = ['KB', 'MB', 'GB'];
  let value = bytes / 1024;
  let unit = 0;
  while (value >= 1024 && unit < units.length - 1) {
    value /= 1024;
    unit++;
  }
  return `${value < 10 ? value.toFixed(1) : Math.round(value)} ${units[unit]}`;
}
