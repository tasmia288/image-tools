/**
 * Format-agnostic image conversion, using only browser-native APIs.
 *
 * One engine drives every tool page: a page declares its source format and
 * target format, and this module handles validation, decoding and encoding.
 *
 * Nothing here performs a network request. Files are read from the user's disk
 * by the browser, decoded by the browser's image decoder, and re-encoded
 * through a canvas. There is no upload path anywhere in this codebase.
 */

/** Widest dimension any mainstream browser will accept for a canvas. */
const MAX_CANVAS_SIDE = 16384;

/** Errors we raise deliberately, so the UI can show them verbatim. */
export class ConversionError extends Error {}

/* ------------------------------------------------------------------ *
 * Format registry
 * ------------------------------------------------------------------ */

const startsWith = (bytes, signature) => signature.every((b, i) => bytes[i] === b);
const ascii = (bytes, start, end) => String.fromCharCode(...bytes.slice(start, end));

/**
 * Each source format knows how to recognise itself from the file's first bytes,
 * so a JPEG renamed to `.png` is caught before it wastes a decode.
 */
export const SOURCE_FORMATS = {
  webp: {
    label: 'WebP',
    extensions: ['webp'],
    mimeTypes: ['image/webp'],
    accept: 'image/webp,.webp',
    // A WebP is a RIFF container whose form type is "WEBP".
    matches: (b) => ascii(b, 0, 4) === 'RIFF' && ascii(b, 8, 12) === 'WEBP',
  },
  png: {
    label: 'PNG',
    extensions: ['png'],
    mimeTypes: ['image/png'],
    accept: 'image/png,.png',
    matches: (b) => startsWith(b, [0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]),
  },
  jpeg: {
    label: 'JPG',
    extensions: ['jpg', 'jpeg', 'jfif', 'pjpeg'],
    mimeTypes: ['image/jpeg'],
    accept: 'image/jpeg,.jpg,.jpeg',
    matches: (b) => startsWith(b, [0xff, 0xd8, 0xff]),
  },
};

export const TARGET_FORMATS = {
  png: { label: 'PNG', mimeType: 'image/png', extension: 'png', lossy: false, alpha: true },
  jpeg: { label: 'JPG', mimeType: 'image/jpeg', extension: 'jpg', lossy: true, alpha: false },
  webp: { label: 'WebP', mimeType: 'image/webp', extension: 'webp', lossy: true, alpha: true },
};

/* ------------------------------------------------------------------ *
 * Encoder support
 * ------------------------------------------------------------------ */

const encoderSupport = new Map();

/**
 * Canvas can always write PNG and JPEG, but WebP encoding is missing from
 * older Safari. Rather than assume, encode one pixel and see what comes back:
 * a browser that cannot honour the type silently falls back to PNG.
 */
export async function canEncode(mimeType) {
  if (encoderSupport.has(mimeType)) return encoderSupport.get(mimeType);

  let supported = false;
  try {
    const canvas = document.createElement('canvas');
    canvas.width = canvas.height = 1;
    const blob = await new Promise((resolve) => canvas.toBlob(resolve, mimeType));
    supported = Boolean(blob) && blob.type === mimeType;
  } catch {
    supported = false;
  }
  encoderSupport.set(mimeType, supported);
  return supported;
}

/* ------------------------------------------------------------------ *
 * Validation
 * ------------------------------------------------------------------ */

const extensionOf = (name) => (name.split('.').pop() || '').toLowerCase();

/** Cheap first pass: does this file even claim to be the right format? */
function claimsToBe(file, format) {
  return format.mimeTypes.includes(file.type) || format.extensions.includes(extensionOf(file.name));
}

/**
 * Confirms the file is really the expected format, by MIME/extension and then
 * by reading its first bytes.
 * @returns {Promise<{ok: true} | {ok: false, reason: string}>}
 */
export async function validateFile(file, format) {
  if (file.size === 0) {
    return { ok: false, reason: 'This file is empty.' };
  }
  if (!claimsToBe(file, format)) {
    const detected = detectFormatLabel(file);
    return {
      ok: false,
      reason: `Not a ${format.label} file${detected ? ` (looks like ${detected})` : ''}. This tool converts ${format.label} images.`,
    };
  }
  if (file.size < 12) {
    return { ok: false, reason: `This file is too small to be a valid ${format.label} image.` };
  }

  const header = new Uint8Array(await file.slice(0, 16).arrayBuffer());
  if (!format.matches(header)) {
    return {
      ok: false,
      reason: `This file is named .${extensionOf(file.name)} but its contents are not a valid ${format.label} image.`,
    };
  }
  return { ok: true };
}

/** Best-effort label for a wrong-format file, purely to write a better error. */
function detectFormatLabel(file) {
  const ext = extensionOf(file.name);
  for (const format of Object.values(SOURCE_FORMATS)) {
    if (format.mimeTypes.includes(file.type) || format.extensions.includes(ext)) return format.label;
  }
  if (file.type.startsWith('image/')) return file.type.replace('image/', '').toUpperCase();
  return '';
}

/* ------------------------------------------------------------------ *
 * Decoding
 * ------------------------------------------------------------------ */

/**
 * `createImageBitmap` is preferred: it decodes off the main thread, so the UI
 * keeps responding on large images. Older Safari falls back to an <img>.
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
      img.onerror = () =>
        reject(new ConversionError('The image could not be decoded. It may be corrupted, or your browser may not support this variant.'));
      img.src = url;
    });
  } finally {
    URL.revokeObjectURL(url);
  }
}

function sizeOf(source) {
  return {
    width: source.width || source.naturalWidth || 0,
    height: source.height || source.naturalHeight || 0,
  };
}

/* ------------------------------------------------------------------ *
 * Encoding
 * ------------------------------------------------------------------ */

async function encode(source, width, height, options) {
  const { target, quality, background } = options;

  const useOffscreen =
    typeof OffscreenCanvas === 'function' &&
    typeof OffscreenCanvas.prototype.convertToBlob === 'function';

  const canvas = useOffscreen
    ? new OffscreenCanvas(width, height)
    : Object.assign(document.createElement('canvas'), { width, height });

  const ctx = canvas.getContext('2d');
  if (!ctx) throw new ConversionError('Your browser could not create a drawing canvas for this image.');

  // JPEG has no alpha channel. Without an opaque base, transparent pixels are
  // written as black, which is never what anyone wants.
  if (!target.alpha) {
    ctx.fillStyle = background || '#ffffff';
    ctx.fillRect(0, 0, width, height);
  }
  ctx.drawImage(source, 0, 0, width, height);

  const args = target.lossy ? [target.mimeType, quality] : [target.mimeType];
  const blob = useOffscreen
    ? await canvas.convertToBlob({ type: target.mimeType, quality: target.lossy ? quality : undefined })
    : await new Promise((resolve) => canvas.toBlob(resolve, ...args));

  if (!blob || blob.size === 0) {
    throw new ConversionError('Encoding failed, most likely because the image is too large for this device.');
  }
  if (blob.type !== target.mimeType) {
    throw new ConversionError(`Your browser cannot write ${target.label} files. Try Chrome, Edge or Firefox.`);
  }
  return blob;
}

/**
 * Converts one validated file to the target format.
 * @param {File} file
 * @param {{target: object, quality?: number, background?: string}} options
 * @returns {Promise<{blob: Blob, width: number, height: number}>}
 */
export async function convertImage(file, options) {
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
    const blob = await encode(source, width, height, options);
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
export function retargetFilename(name, extension) {
  const base = (name.split(/[\\/]/).pop() || 'image').replace(/\.[^.]+$/, '');
  return `${base || 'image'}.${extension}`;
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

/** Signed percentage change from one size to another, e.g. "+340%" / "−62%". */
export function sizeDelta(from, to) {
  if (!from || !to) return '';
  const change = Math.round(((to - from) / from) * 100);
  if (change === 0) return 'same size';
  return change > 0 ? `+${change}% larger` : `${Math.abs(change)}% smaller`;
}
