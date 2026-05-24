import React from "react";
// import PDFViewer from "pdf-viewer-reactjs";
const Forms = () =>{

    return (
        <>
        {/* <div style={{ height: "90vh" }}>
        <PDFViewer
        document={{
          url: "../assets/files/Air Safety Report.pdf",
        }}
      />
    </div> */}
    <div style={{ width: "100%", height: "100vh" }}>
      <iframe
        src="/Air Safety Report.pdf"
        style={{ width: "100%", height: "100%", border: "none" }}
        title="PDF Viewer"
      />
    </div>
        </>
    )
}
export default Forms