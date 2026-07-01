import { useEffect, useState } from "react";
import usePdfCache from "../../hooks/usePdfCache";

const PDFViewer = ({ manual }) => {
  const { getPdf } = usePdfCache();

  const [url, setUrl] = useState(null);
  const [loadError, setLoadError] = useState(null);

  useEffect(() => {
    if (!manual) {
      setUrl(null);
      setLoadError(null);
      return;
    }

    let active = true;

    setUrl(null);
    setLoadError(null);

    getPdf(manual)
      .then((pdfUrl) => {
        if (active) setUrl(pdfUrl);
      })
      .catch((err) => {
        console.error("PDF load error:", err);
        if (active) setLoadError(err?.message || "PDF load failed");
      });

    return () => {
      active = false;
    };
  }, [manual]);

  if (!manual) return <p>Select a document</p>;

  if (loadError) {
    return (
      <div style={{ padding: 16 }}>
        <p>PDF load error: {loadError}</p>
      </div>
    );
  }

  if (!url) return <p>Loading PDF...</p>;

  return (
    <div style={{ width: "100%", height: "100%", background: "#eaeaea" }}>
      <iframe
        src={`${url}#toolbar=1&navpanes=0`}
        title={manual.title || "PDF Document"}
        style={{
          width: "100%",
          height: "100%",
          border: "none",
          background: "#fff",
        }}
      />
    </div>
  );
};

export default PDFViewer;
