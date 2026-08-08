/**
 * Minimal ZIP writer - "stored" (no compression) entries only.
 *
 * Why hand-rolled instead of a library: PNG data is already DEFLATE-compressed
 * internally, so zipping it again saves almost nothing. Storing the bytes as-is
 * keeps this to ~120 lines and adds zero download weight or third-party code.
 *
 * Produces a standard ZIP readable by Windows Explorer, macOS Archive Utility,
 * unzip(1) and 7-Zip. Limited to archives below 4 GB (no ZIP64).
 */

const LOCAL_SIG = 0x04034b50;
const CENTRAL_SIG = 0x02014b50;
const EOCD_SIG = 0x06054b50;
const UTF8_FLAG = 0x0800;
const MAX_ZIP_BYTES = 0xffffffff; // ZIP64 would be required beyond this.

let crcTable = null;

function getCrcTable() {
  if (crcTable) return crcTable;
  crcTable = new Uint32Array(256);
  for (let i = 0; i < 256; i++) {
    let c = i;
    for (let bit = 0; bit < 8; bit++) {
      c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
    }
    crcTable[i] = c >>> 0;
  }
  return crcTable;
}

function crc32(bytes) {
  const table = getCrcTable();
  let crc = 0xffffffff;
  for (let i = 0; i < bytes.length; i++) {
    crc = table[(crc ^ bytes[i]) & 0xff] ^ (crc >>> 8);
  }
  return (crc ^ 0xffffffff) >>> 0;
}

/** MS-DOS packed date/time, as the ZIP spec requires. */
function dosDateTime(date) {
  const year = Math.max(1980, date.getFullYear());
  return {
    time: (date.getHours() << 11) | (date.getMinutes() << 5) | (date.getSeconds() >> 1),
    date: ((year - 1980) << 9) | ((date.getMonth() + 1) << 5) | date.getDate(),
  };
}

/**
 * @param {Array<{name: string, blob: Blob}>} files
 * @returns {Promise<Blob>} a ZIP archive
 */
export async function createZip(files) {
  const encoder = new TextEncoder();
  const now = dosDateTime(new Date());
  const chunks = [];
  const central = [];
  let offset = 0;

  for (const file of files) {
    const nameBytes = encoder.encode(file.name);
    const data = new Uint8Array(await file.blob.arrayBuffer());
    const crc = crc32(data);

    const header = new Uint8Array(30 + nameBytes.length);
    const view = new DataView(header.buffer);
    view.setUint32(0, LOCAL_SIG, true);
    view.setUint16(4, 20, true);          // version needed to extract
    view.setUint16(6, UTF8_FLAG, true);   // filenames are UTF-8
    view.setUint16(8, 0, true);           // method: stored
    view.setUint16(10, now.time, true);
    view.setUint16(12, now.date, true);
    view.setUint32(14, crc, true);
    view.setUint32(18, data.length, true); // compressed size
    view.setUint32(22, data.length, true); // uncompressed size
    view.setUint16(26, nameBytes.length, true);
    view.setUint16(28, 0, true);           // extra field length
    header.set(nameBytes, 30);

    chunks.push(header, data);
    central.push({ nameBytes, crc, size: data.length, offset });

    offset += header.length + data.length;
    if (offset > MAX_ZIP_BYTES) {
      throw new Error('The archive would exceed 4 GB. Download the images individually instead.');
    }
  }

  const directoryOffset = offset;
  let directorySize = 0;

  for (const entry of central) {
    const record = new Uint8Array(46 + entry.nameBytes.length);
    const view = new DataView(record.buffer);
    view.setUint32(0, CENTRAL_SIG, true);
    view.setUint16(4, 20, true);          // version made by
    view.setUint16(6, 20, true);          // version needed
    view.setUint16(8, UTF8_FLAG, true);
    view.setUint16(10, 0, true);          // method: stored
    view.setUint16(12, now.time, true);
    view.setUint16(14, now.date, true);
    view.setUint32(16, entry.crc, true);
    view.setUint32(20, entry.size, true);
    view.setUint32(24, entry.size, true);
    view.setUint16(28, entry.nameBytes.length, true);
    // bytes 30-42: extra len, comment len, disk number, attributes - all zero
    view.setUint32(42, entry.offset, true);
    record.set(entry.nameBytes, 46);

    chunks.push(record);
    directorySize += record.length;
  }

  const eocd = new Uint8Array(22);
  const eocdView = new DataView(eocd.buffer);
  eocdView.setUint32(0, EOCD_SIG, true);
  eocdView.setUint16(8, central.length, true);   // entries on this disk
  eocdView.setUint16(10, central.length, true);  // total entries
  eocdView.setUint32(12, directorySize, true);
  eocdView.setUint32(16, directoryOffset, true);
  chunks.push(eocd);

  return new Blob(chunks, { type: 'application/zip' });
}
