import { useEffect, useState } from "react";

export default function usePdfHighlights(manualId) {
  const key = `pdf-highlights-${manualId}`;

  const [highlights, setHighlights] = useState([]);

  useEffect(() => {
    if (!manualId) return;

    const saved = localStorage.getItem(key);
    setHighlights(saved ? JSON.parse(saved) : []);
  }, [manualId]);

  const addHighlight = (highlight) => {
    setHighlights((prev) => {
      const updated = [...prev, highlight];
      localStorage.setItem(key, JSON.stringify(updated));
      return updated;
    });
  };

  const clearHighlights = () => {
    localStorage.removeItem(key);
    setHighlights([]);
  };

  return {
    highlights,
    addHighlight,
    clearHighlights,
  };
}
