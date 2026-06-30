// import { useEffect } from "react";
// import { downloadManual } from "../services/apiService";

// import {
//   getCachedPdf,
//   addPdf,
//   hasPendingDownload,
//   getPendingDownload,
//   setPendingDownload,
//   clearPendingDownload,
//   clearPdfCache,
// } from "../services/pdfCache";

// export default function usePdfCache() {
//   const getPdf = async (manual) => {
//     const cached = getCachedPdf(manual.id);

//     if (cached) {
//       return cached;
//     }

//     if (hasPendingDownload(manual.id)) {
//       return getPendingDownload(manual.id);
//     }

//     const promise = downloadManual(manual.id)
//       .then((blob) => {
//         const url = URL.createObjectURL(blob);

//         addPdf(manual.id, url);

//         clearPendingDownload(manual.id);

//         return url;
//       })
//       .catch((err) => {
//         clearPendingDownload(manual.id);

//         throw err;
//       });

//     setPendingDownload(manual.id, promise);

//     return promise;
//   };

//   useEffect(() => {
//     return () => {
//       clearPdfCache();
//     };
//   }, []);

//   return {
//     getPdf,
//   };
// }

import { useRef } from "react";
import { downloadManual } from "../services/apiService";

const MAX_CACHE = 5;

export default function usePdfCache() {
  const cache = useRef(new Map());
  const loading = useRef(new Map());

  const getPdf = async (manual) => {
    const id = manual.id;

    // 1. return cached
    if (cache.current.has(id)) {
      const url = cache.current.get(id);

      // LRU refresh
      cache.current.delete(id);
      cache.current.set(id, url);

      return url;
    }

    // 2. prevent duplicate downloads
    if (loading.current.has(id)) {
      return loading.current.get(id);
    }

    const promise = downloadManual(id)
      .then((blob) => {
        const url = URL.createObjectURL(blob);

        cache.current.set(id, url);

        // LRU eviction
        if (cache.current.size > MAX_CACHE) {
          const firstKey = cache.current.keys().next().value;
          const oldUrl = cache.current.get(firstKey);

          URL.revokeObjectURL(oldUrl);
          cache.current.delete(firstKey);
        }

        loading.current.delete(id);
        return url;
      })
      .catch((err) => {
        loading.current.delete(id);
        throw err;
      });

    loading.current.set(id, promise);

    return promise;
  };

  return { getPdf };
}
