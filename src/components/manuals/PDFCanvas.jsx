import { Document, Page } from "react-pdf";

const PDFCanvas = ({
  url,
  numPages,
  setNumPages,
  zoom,
  setCurrentPage,
}) => {

    return (
        <Document
            file={url}
            onLoadSuccess={({ numPages }) => setNumPages(numPages)}
        >
            {Array.from({ length: numPages || 0 }).map((_, index) => (
                <div
                    key={index}
                    className="pdf-page-wrapper"
                    data-page-number={index + 1}
                    style={{
                        position: "relative",
                        display: "flex",
                        justifyContent: "center",
                        marginBottom: 16,
                    }}
                >
                    <Page
                        pageNumber={index + 1}
                        scale={zoom}
                        renderTextLayer
                        renderAnnotationLayer={false}
                    />
                </div>
            ))}
        </Document>
    );
};

export default PDFCanvas;