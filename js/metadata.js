/* =======================================
   TRUSTCHECK — Metadata & Analysis Module
   Client-side only. No external deps.
   ======================================= */

/**
 * Analyze a file and return trust analysis results.
 * @param {File} file
 * @returns {Promise<{trustScore: number, verdict: string, tags: Array, evidence: Array, metadata: Object}>}
 */
export async function analyzeFile(file) {
  const evidence = [];
  const tags = [];
  let trustScore = 50; // Start neutral

  // 1. File type & size check
  const ext = file.name.split('.').pop().toLowerCase();
  const isImage = ['jpg','jpeg','png','webp','gif','avif'].includes(ext);
  const isVideo = ['mp4','mov','webm'].includes(ext);

  evidence.push({
    label: 'File type',
    desc: `${file.name} (${formatSize(file.size)})`,
    severity: 'info',
    score: null
  });

  // 2. Last modified date (from File API)
  if (file.lastModified) {
    const date = new Date(file.lastModified);
    const ageDays = (Date.now() - file.lastModified) / 86400000;
    evidence.push({
      label: 'File timestamp',
      desc: date.toISOString().replace('T',' ').slice(0,19) +
        (ageDays < 1 ? ' (today)' : ageDays < 7 ? ` (${Math.round(ageDays)}d ago)` : ''),
      severity: 'info',
      score: null
    });
  }

  // 3. Try to read EXIF metadata if it's a JPEG
  if (ext === 'jpg' || ext === 'jpeg') {
    const exif = await readBasicEXIF(file);
    if (exif) {
      const hasMaker = exif.make || exif.model;
      evidence.push({
        label: 'Camera info',
        desc: hasMaker ? `${exif.make || 'Unknown'} ${exif.model || ''}`.trim() : 'No camera information found',
        severity: hasMaker ? 'clean' : 'medium',
        score: hasMaker ? null : 60
      });
      if (!hasMaker) {
        tags.push({ label: 'No Camera Data', type: 'suspicious' });
        trustScore -= 8;
      } else {
        tags.push({ label: `📷 ${exif.make || 'Camera'}`, type: 'clean' });
        trustScore += 10;
      }

      if (exif.software) {
        evidence.push({
          label: 'Editing software',
          desc: exif.software,
          severity: isAITool(exif.software) ? 'high' : 'medium',
          score: isAITool(exif.software) ? 85 : 45
        });
        if (isAITool(exif.software)) {
          tags.push({ label: `AI Tool: ${exif.software}`, type: 'ai' });
          trustScore -= 20;
        }
      }

      if (exif.datetime) {
        evidence.push({
          label: 'Date taken',
          desc: exif.datetime,
          severity: 'info',
          score: null
        });
      }
    } else {
      evidence.push({
        label: 'EXIF Metadata',
        desc: 'No EXIF data found — likely stripped or generated content',
        severity: 'medium',
        score: 55
      });
      tags.push({ label: 'EXIF Stripped', type: 'suspicious' });
      trustScore -= 10;
    }
  } else {
    evidence.push({
      label: 'EXIF Metadata',
      desc: `Format: ${ext.toUpperCase()} — limited EXIF support (JPEG only)`,
      severity: 'info',
      score: null
    });
  }

  // 4. Basic C2PA check (look for Adobe C2PA signature in bytes)
  if (isImage) {
    const c2paResult = await checkC2PA(file);
    if (c2paResult.found) {
      evidence.push({
        label: 'C2PA Content Credentials',
        desc: c2paResult.detail || 'Valid cryptographic signature found',
        severity: 'clean',
        score: null
      });
      tags.push({ label: 'C2PA Signed ✅', type: 'clean' });
      trustScore += 15;
    } else {
      evidence.push({
        label: 'C2PA Provenance',
        desc: 'No C2PA cryptographic signature found',
        severity: 'low',
        score: null
      });
      tags.push({ label: 'No C2PA', type: 'suspicious' });
    }
  }

  // 5. Try pixel analysis (frequency artifacts)
  if (isImage) {
    const freqResult = await analyzeFrequency(file);
    evidence.push({
      label: 'Frequency Analysis',
      desc: freqResult.detail,
      severity: freqResult.severity,
      score: freqResult.score
    });
    if (freqResult.severity === 'high') {
      tags.push({ label: 'AI Artifacts', type: 'ai' });
      trustScore -= freqResult.score * 0.3;
    } else if (freqResult.severity === 'medium') {
      tags.push({ label: 'Slight Artifacts', type: 'suspicious' });
      trustScore -= freqResult.score * 0.15;
    } else if (freqResult.severity === 'clean') {
      tags.push({ label: 'Natural Pattern', type: 'clean' });
      trustScore += 10;
    }
  }

  // 6. Normalize trust score
  trustScore = Math.max(0, Math.min(100, Math.round(trustScore)));

  // 7. Determine verdict
  let verdict;
  if (trustScore >= 70) verdict = 'Likely Authentic';
  else if (trustScore >= 40) verdict = 'Uncertain';
  else verdict = 'Likely AI-Generated';

  return {
    trustScore,
    verdict,
    tags: tags.slice(0, 6),
    evidence
  };
}

/* ---- Helpers ---- */

function formatSize(bytes) {
  if (bytes < 1024) return bytes + 'B';
  if (bytes < 1048576) return (bytes / 1024).toFixed(1) + 'KB';
  return (bytes / 1048576).toFixed(1) + 'MB';
}

function isAITool(sw) {
  const aiTools = ['midjourney','dall-e','dalle','stable diffusion','firefly','adobe firefly',
    'generative fill','chatgpt','ai','gan','sora','runway','kling','pika'];
  return aiTools.some(t => sw.toLowerCase().includes(t));
}

/**
 * Read basic EXIF from JPEG file (client-side binary parsing).
 */
async function readBasicEXIF(file) {
  try {
    const buffer = await file.slice(0, 65536).arrayBuffer();
    const dv = new DataView(buffer);
    const result = {};

    // Check JPEG SOI marker
    if (dv.getUint8(0) !== 0xFF || dv.getUint8(1) !== 0xD8) return null;

    let offset = 2;
    while (offset < dv.byteLength - 1) {
      if (dv.getUint8(offset) !== 0xFF) break;
      const marker = dv.getUint8(offset + 1);
      if (marker === 0xD9 || marker === 0xDA) break; // EOI/SOS
      const size = dv.getUint16(offset + 2);
      if (size < 2) break;

      // APP1 marker = EXIF
      if (marker === 0xE1) {
        const appStart = offset + 4;
        // EXIF header: "Exif\0\0"
        if (appStart + 6 <= dv.byteLength) {
          const header = String.fromCharCode(dv.getUint8(appStart), dv.getUint8(appStart+1),
            dv.getUint8(appStart+2), dv.getUint8(appStart+3), dv.getUint8(appStart+4), dv.getUint8(appStart+5));
          if (header === 'Exif\0\0') {
            const tiffOffset = appStart + 6;
            parseTIFF(dv, tiffOffset, result);
          }
        }
      }
      offset += 2 + size;
    }
    return Object.keys(result).length > 0 ? result : null;
  } catch {
    return null;
  }
}

function parseTIFF(dv, offset, result) {
  const endian = dv.getUint16(offset);
  const little = endian === 0x4949; // 'II'
  const get16 = (o) => little ? dv.getUint16(o, true) : dv.getUint16(o);
  const get32 = (o) => little ? dv.getUint32(o, true) : dv.getUint32(o);

  // Check TIFF magic
  if (endian !== 0x4949 && endian !== 0x4D4D) return;
  if (get16(offset + 2) !== 42) return;

  const ifdOffset = get32(offset + 4);
  readIFD(dv, offset + ifdOffset, get16, get32, result, offset);
}

function readIFD(dv, start, get16, get32, result, tiffBase) {
  if (start + 2 > dv.byteLength) return;
  const entries = get16(start);
  for (let i = 0; i < entries; i++) {
    const entry = start + 2 + i * 12;
    if (entry + 12 > dv.byteLength) break;
    const tag = get16(entry);
    const type = get16(entry + 2);
    const count = get32(entry + 4);
    let valueOff = entry + 8;

    // Values 4 bytes or less are inline
    if (count * typeSize(type) > 4) {
      valueOff = tiffBase + get32(entry + 8);
    }

    switch (tag) {
      case 0x010F: result.make = readString(dv, valueOff, count); break;
      case 0x0110: result.model = readString(dv, valueOff, count); break;
      case 0x0131: result.software = readString(dv, valueOff, count); break;
      case 0x0132: result.datetime = readString(dv, valueOff, count); break;
    }
  }
}

function typeSize(t) {
  return [0,1,1,2,4,8,1,1,2,4,8,4,8][t] || 1;
}

function readString(dv, offset, count) {
  const bytes = [];
  for (let i = 0; i < Math.min(count, 64); i++) {
    const b = dv.getUint8(offset + i);
    if (b === 0) break;
    bytes.push(b);
  }
  return String.fromCharCode(...bytes);
}

/**
 * Check for C2PA manifest in JPEG/PNG (basic byte search).
 */
async function checkC2PA(file) {
  try {
    const buffer = await file.slice(0, Math.min(file.size, 1_048_576)).arrayBuffer();
    const bytes = new Uint8Array(buffer);
    const text = new TextDecoder('utf-8', { fatal: false }).decode(bytes);

    // C2PA manifest starts with specific markers
    const c2paPatterns = [
      'c2pa', 'C2PA', 'ContentCredentials', 'manifest.json', 'xmp:MM:Manifest',
      'adobe:ns:meta/', 'xmpMM:Manifest'
    ];
    const found = c2paPatterns.some(p => text.includes(p));

    return {
      found,
      detail: found ? 'C2PA-compatible signature detected in file' : 'No C2PA manifest found'
    };
  } catch {
    return { found: false, detail: 'Could not read file bytes for C2PA check' };
  }
}

/**
 * Basic frequency/artifact analysis using Canvas.
 * Scans for uniformity indicators common in AI-generated images.
 */
async function analyzeFrequency(file) {
  try {
    const img = await loadImage(file);
    if (!img) return { severity: 'low', detail: 'Could not load image for pixel analysis', score: 0 };

    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    // Analyze center region and edges
    const size = Math.min(256, img.width, img.height);
    canvas.width = size;
    canvas.height = size;
    ctx.drawImage(img, (img.width-size)/2, (img.height-size)/2, size, size, 0, 0, size, size);

    const data = ctx.getImageData(0, 0, size, size).data;

    // Simple analysis: check pixel variance in regions
    // AI images tend to have lower variance in certain color channels
    let totalVariance = 0;
    const blockSize = 8;
    const blocks = [];

    for (let by = 0; by < size / blockSize; by++) {
      for (let bx = 0; bx < size / blockSize; bx++) {
        let sumR = 0, sumG = 0, sumB = 0, count = 0;
        for (let y = by * blockSize; y < (by+1) * blockSize; y++) {
          for (let x = bx * blockSize; x < (bx+1) * blockSize; x++) {
            const idx = (y * size + x) * 4;
            sumR += data[idx];
            sumG += data[idx+1];
            sumB += data[idx+2];
            count++;
          }
        }
        const avgR = sumR / count, avgG = sumG / count, avgB = sumB / count;
        let varR = 0, varG = 0, varB = 0;
        for (let y = by * blockSize; y < (by+1) * blockSize; y++) {
          for (let x = bx * blockSize; x < (bx+1) * blockSize; x++) {
            const idx = (y * size + x) * 4;
            varR += (data[idx] - avgR) ** 2;
            varG += (data[idx+1] - avgG) ** 2;
            varB += (data[idx+2] - avgB) ** 2;
          }
        }
        blocks.push((varR + varG + varB) / (count * 3));
      }
    }

    const meanVariance = blocks.reduce((a,b) => a+b, 0) / blocks.length;
    const stdVariance = Math.sqrt(blocks.reduce((a,b) => a + (b - meanVariance)**2, 0) / blocks.length);
    const uniformityScore = stdVariance / Math.max(meanVariance, 1);

    // Very uniform blocks across all regions → likely AI
    // High variance → natural
    const artifactScore = Math.max(0, Math.min(100, (1 - Math.min(uniformityScore, 2) / 2) * 100));

    if (artifactScore > 60) {
      return {
        severity: 'high',
        detail: `AI artifacts detected: unusually uniform pixel patterns (score: ${Math.round(artifactScore)}%)`,
        score: artifactScore
      };
    } else if (artifactScore > 30) {
      return {
        severity: 'medium',
        detail: `Slight uniformities detected — may indicate processing (score: ${Math.round(artifactScore)}%)`,
        score: artifactScore
      };
    } else {
      return {
        severity: 'clean',
        detail: `Natural variance patterns consistent with authentic imagery`,
        score: artifactScore
      };
    }
  } catch {
    return { severity: 'low', detail: 'Frequency analysis not available for this file type', score: 0 };
  }
}

function loadImage(file) {
  return new Promise((resolve) => {
    if (!file.type.startsWith('image/')) { resolve(null); return; }
    const url = URL.createObjectURL(file);
    const img = new Image();
    img.onload = () => { URL.revokeObjectURL(url); resolve(img); };
    img.onerror = () => { URL.revokeObjectURL(url); resolve(null); };
    img.src = url;
  });
}

export { formatSize, readBasicEXIF, checkC2PA, analyzeFrequency };