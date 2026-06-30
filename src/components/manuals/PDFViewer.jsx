import { useEffect, useState, useRef } from "react";
// import { Document, Page, pdfjs } from "react-pdf";
import { pdfjs } from "react-pdf";
import usePdfCache from "../../hooks/usePdfCache";
import PDFToolbar from "./PDFToolbar";
import PDFCanvas from "./PDFCanvas";

pdfjs.GlobalWorkerOptions.workerSrc = new URL(
  "pdfjs-dist/build/pdf.worker.min.mjs",
  import.meta.url
).toString();

const PDFViewer = ({ manual }) => {
  const { getPdf } = usePdfCache();
const [currentPage, setCurrentPage] = useState(1);

  const containerRef = useRef(null);

  const [url, setUrl] = useState(null);
  const [numPages, setNumPages] = useState(null);

  const [zoom, setZoom] = useState(1);
  const [fitMode, setFitMode] = useState("width"); 
useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    const onScroll = () => {
        const pages = container.querySelectorAll(".pdf-page-wrapper");

        let visible = 1;
        let minDistance = Infinity;

        pages.forEach((page) => {
            const rect = page.getBoundingClientRect();

            const distance = Math.abs(rect.top - 120);

            if (distance < minDistance) {
                minDistance = distance;
                visible = Number(page.dataset.pageNumber);
            }
        });

        setCurrentPage(visible);
    };

    container.addEventListener("scroll", onScroll);

    onScroll();

    return () => container.removeEventListener("scroll", onScroll);
}, [numPages]);
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

  
  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;

    const onWheel = (e) => {
      if (!e.ctrlKey) return;

      e.preventDefault();

      setZoom((z) => {
        const next = z - e.deltaY * 0.001;
        return Math.min(2.5, Math.max(0.6, next));
      });
    };

    el.addEventListener("wheel", onWheel, { passive: false });

    return () => el.removeEventListener("wheel", onWheel);
  }, []);

  const getScale = (pageWidth) => {
    if (fitMode === "page") return 1.2;

    if (fitMode === "width" && containerRef.current) {
      const containerWidth = containerRef.current.offsetWidth;
      return (containerWidth / pageWidth) * zoom;
    }

    return zoom;
  };

  if (!manual) return <p>Select a document</p>;
  if (!url) return <p>Loading PDF...</p>;

  return (
    <div style={{ height: "100%", display: "flex", flexDirection: "column" }}>

<PDFToolbar
    zoom={zoom}
    setZoom={setZoom}
    fitMode={fitMode}
    setFitMode={setFitMode}
    currentPage={currentPage}
    numPages={numPages}
/>

      
      <div
  ref={containerRef}
  style={{
    flex: 1,
    overflow: "auto",
    background: "#eaeaea",
    padding: "16px",
  }}
>
        {/* <Document
          file={url}
          onLoadSuccess={({ numPages }) => setNumPages(numPages)}
        >
          {Array.from(new Array(numPages), (_, i) => (
            <div
              key={i}
              style={{
                position:'relative',
                display: "flex",
                justifyContent: "center",
                marginBottom: 12,
              }}
            >
              <Page
                pageNumber={i + 1}
                scale={zoom}
                renderTextLayer={true}
                renderAnnotationLayer={false}
              />
            </div>
          ))}
        </Document> */}
        <PDFCanvas
    url={url}
    zoom={zoom}
    numPages={numPages}
    setNumPages={setNumPages}
/>
      </div>
    </div>
  );
};

export default PDFViewer;