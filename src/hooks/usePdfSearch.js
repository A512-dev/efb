import { useState } from "react";

export default function usePdfSearch(pdf) {
  const [results, setResults] = useState([]);
  const [current, setCurrent] = useState(0);
  const [loading, setLoading] = useState(false);

  const search = async (query) => {
    if (!pdf || !query.trim()) {
      setResults([]);
      setCurrent(0);
      return;
    }

    setLoading(true);

    const matches = [];

    for (let page = 1; page <= pdf.numPages; page++) {
      const pdfPage = await pdf.getPage(page);

      const text = await pdfPage.getTextContent();

      const fullText = text.items.map((item) => item.str).join(" ");

      if (fullText.toLowerCase().includes(query.toLowerCase())) {
        matches.push({
          page,
          text: fullText,
        });
      }
    }

    setResults(matches);
    setCurrent(matches.length ? 1 : 0);

    setLoading(false);
  };

  return {
    results,
    current,
    setCurrent,
    search,
    loading,
  };
}
