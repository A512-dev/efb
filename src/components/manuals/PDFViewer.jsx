import { useEffect, useState } from "react";
import { Document, Page, pdfjs } from "react-pdf";
import usePdfCache from "../../hooks/usePdfCache";

pdfjs.GlobalWorkerOptions.workerSrc = new URL(
  "pdfjs-dist/build/pdf.worker.min.mjs",
  import.meta.url
).toString();

const PDFViewer = ({ manual }) => {
  const { getPdf } = usePdfCache();

  const [url, setUrl] = useState(null);
  const [numPages, setNumPages] = useState(null);
  const [scale] = useState(1.2);

  useEffect(() => {
    if (!manual) {
      setUrl(null);
      return;
    }

    let active = true;

    getPdf(manual)
      .then((u) => {
        if (active) setUrl(u);
      })
      .catch(console.error);

    return () => {
      active = false;
    };
  }, [manual]);

  if (!manual) return <p>Select a document</p>;
  if (!url) return <p>Loading PDF...</p>;

  return (
    <div
      style={{
        height: "100%",
        overflowY: "auto",
        padding: "16px",
        background: "#f5f5f5",
      }}
    >
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          gap: "12px",
        }}
      >
        <Document
          file={url}
          onLoadSuccess={({ numPages }) => setNumPages(numPages)}
        >
          {Array.from(new Array(numPages), (_, i) => (
            <div
              key={i}
              style={{
                boxShadow: "0 2px 10px rgba(0,0,0,0.1)",
                background: "white",
              }}
            >
              <Page
                pageNumber={i + 1}
                scale={scale}
                renderTextLayer={false}
                renderAnnotationLayer={false}
              />
            </div>
          ))}
        </Document>
      </div>
    </div>
  );
};

export default PDFViewer;