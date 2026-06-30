const PDFToolbar = ({
  zoom,
  setZoom,
  fitMode,
  setFitMode,
  currentPage,
  numPages,
}) => {
  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        gap: 12,
        padding: "10px 14px",
        borderBottom: "1px solid #ddd",
        background: "#f9f9f9",
        position: "sticky",
        top: 0,
        zIndex: 100,
      }}
    >
      <button onClick={() => setZoom((z) => Math.max(0.6, z - 0.2))}>
        −
      </button>

      <span style={{ minWidth: 60, textAlign: "center" }}>
        {Math.round(zoom * 100)}%
      </span>

      <button onClick={() => setZoom((z) => Math.min(2.5, z + 0.2))}>
        +
      </button>

      <button onClick={() => setZoom(1)}>
        Reset
      </button>

      <div
        style={{
          width: 1,
          height: 22,
          background: "#ccc",
        }}
      />

      <button
        onClick={() => setFitMode("width")}
        style={{
          fontWeight: fitMode === "width" ? "bold" : "normal",
        }}
      >
        Fit Width
      </button>

      <button
        onClick={() => setFitMode("page")}
        style={{
          fontWeight: fitMode === "page" ? "bold" : "normal",
        }}
      >
        Fit Page
      </button>

      <div style={{ marginLeft: "auto" }}>
        Page {currentPage} / {numPages || "-"}
      </div>
    </div>
  );
};

export default PDFToolbar;