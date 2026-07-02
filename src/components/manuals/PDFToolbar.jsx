import {
  ZoomIn,
  ZoomOut,
  RotateCcw,
  ArrowUp,
  ArrowDown,
  ScanSearch,
  Maximize,Search,
  RectangleHorizontal,
} from "lucide-react";
const PDFToolbar = ({
    zoom,
    setZoom,
    fitMode,
    setFitMode,
    currentPage,
    numPages,
searchResults,currentResult,
setCurrentResult, 
    searchText,
    setSearchText,
    search,
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
        <ZoomOut size={18} />
      </button>

      <span style={{ minWidth: 60, textAlign: "center" }}>
        {Math.round(zoom * 100)}%
      </span>

      <button onClick={() => setZoom((z) => Math.min(2.5, z + 0.2))}>
        <ZoomIn size={18} />
      </button>

      <button onClick={() => setZoom(1)}>
        <RotateCcw size={18} />
      </button>

      <div
        style={{
          width: 1,
          height: 22,
          background: "#ccc",
        }}
      />

      <button
  title="Fit Width"
  onClick={() => setFitMode("width")}
>
  <RectangleHorizontal size={18} />
</button>

<button
  title="Fit Page"
  onClick={() => setFitMode("page")}
>
  <Maximize size={18} />
</button>

      <div style={{ marginLeft: "auto" }}>
        Page {currentPage} / {numPages || "-"}
      </div>
      <Search size={16} />
      <div
    style={{
        display: "flex",
        alignItems: "center",
        gap: 6,
        marginLeft: 20,
    }}
>
    <input
    type="text"
    value={searchText}
    onChange={(e) => setSearchText(e.target.value)}
    onKeyDown={(e) => {
        if (e.key === "Enter") {
            search(searchText);
        }
    }}
    placeholder="Search..."
/>

    <button
        disabled={!searchResults.length}
        onClick={() =>
            setCurrentResult((r) =>
                Math.max(r - 1, 0)
            )
        }
    >
        <ArrowUp size={18} />
    </button>

    <button
        disabled={!searchResults.length}
        onClick={() =>
            setCurrentResult((r) =>
                Math.min(r + 1, searchResults.length - 1)
            )
        }
    >
     <ArrowDown size={18} />
    </button>

    <span>
        {searchResults.length
            ? `${currentResult + 1}/${searchResults.length}`
            : "0/0"}
    </span>
</div>
    </div>
  );
};

export default PDFToolbar;