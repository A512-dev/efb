import { Document, Page } from "react-pdf";

const PDFCanvas = ({
  url,
  numPages,
  setNumPages,
  zoom,
  setPdf,
}) => {

    return (
        <Document
    file={url}
    onLoadSuccess={(doc) => {
        setNumPages(doc.numPages);
        setPdf(doc);
    }}
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
                        renderTextLayer={true}
                        renderAnnotationLayer={false}
                    />
                </div>
            ))}
        </Document>
    );
};

export default PDFCanvas;