import { useRef } from "react";
import { downloadManual } from "../services/apiService";

const MAX_CACHE_SIZE = 8;

const pdfCache = new Map();
const pendingRequests = new Map();

export default function usePdfCache() {
  const cacheRef = useRef(pdfCache);

  const getPdf = async (manual) => {
    const id = manual.id;

    if (cacheRef.current.has(id)) {
      const url = cacheRef.current.get(id);

      cacheRef.current.delete(id);
      cacheRef.current.set(id, url);

      return url;
    }

    if (pendingRequests.has(id)) {
      return pendingRequests.get(id);
    }

    const promise = downloadManual(id)
      .then((blob) => {
        const pdfBlob =
          blob instanceof Blob && blob.type === "application/pdf"
            ? blob
            : new Blob([blob], { type: "application/pdf" });

        const url = URL.createObjectURL(pdfBlob);

        cacheRef.current.set(id, url);

        if (cacheRef.current.size > MAX_CACHE_SIZE) {
          const oldestKey = cacheRef.current.keys().next().value;
          const oldUrl = cacheRef.current.get(oldestKey);

          URL.revokeObjectURL(oldUrl);
          cacheRef.current.delete(oldestKey);
        }

        pendingRequests.delete(id);
        return url;
      })
      .catch((err) => {
        pendingRequests.delete(id);
        throw err;
      });

    pendingRequests.set(id, promise);

    return promise;
  };

  return { getPdf };
}
