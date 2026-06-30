const MAX_CACHE_SIZE = 5;

const pdfCache = new Map();
const pendingDownloads = new Map();

export function getCachedPdf(manualId) {
  if (!pdfCache.has(manualId)) return null;

  const url = pdfCache.get(manualId);

  pdfCache.delete(manualId);
  pdfCache.set(manualId, url);

  return url;
}

export function addPdf(manualId, url) {
  if (pdfCache.has(manualId)) {
    pdfCache.delete(manualId);
  }

  pdfCache.set(manualId, url);

  if (pdfCache.size > MAX_CACHE_SIZE) {
    const oldestKey = pdfCache.keys().next().value;
    const oldestUrl = pdfCache.get(oldestKey);

    URL.revokeObjectURL(oldestUrl);

    pdfCache.delete(oldestKey);
  }
}

export function hasPendingDownload(manualId) {
  return pendingDownloads.has(manualId);
}

export function getPendingDownload(manualId) {
  return pendingDownloads.get(manualId);
}

export function setPendingDownload(manualId, promise) {
  pendingDownloads.set(manualId, promise);
}

export function clearPendingDownload(manualId) {
  pendingDownloads.delete(manualId);
}

export function clearPdfCache() {
  pdfCache.forEach((url) => URL.revokeObjectURL(url));

  pdfCache.clear();
  pendingDownloads.clear();
}
