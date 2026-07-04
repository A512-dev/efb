

import React, { useState, useEffect } from 'react';
import { NavLink } from 'react-router-dom';
import { useBookmark } from '../Context/BookmarkContext'; 
import { useManuals } from "../hooks/useManuals";
import { downloadManual } from "../services/apiService";
import PageWrapper from '../components/PageWrapper';

import { DragDropContext, Droppable, Draggable } from "@hello-pangea/dnd";
import { LoaderCircle } from "lucide-react";
import bookmarkRemoveIcon from "../assets/icons/bookmarkpor.svg";

const Clipboard = () => {
  const { clipboardItems, toggleClipboardItem, setClipboardItems } = useBookmark();
  const { loading } = useManuals();
  
  const [openDoc, setOpenDoc] = useState(null);
const [loadingPdf, setLoadingPdf] = useState(false);
const [pdfProgress, setPdfProgress] = useState(10);
  const openManual = async (manual) => {
  try {
    setLoadingPdf(true);
    setPdfProgress(10);

    const timer = setInterval(() => {
      setPdfProgress((prev) => (prev < 90 ? prev + 10 : prev));
    }, 150);

    const blob = await downloadManual(manual.id);
    const url = URL.createObjectURL(blob);

    clearInterval(timer);

    if (openDoc) {
      URL.revokeObjectURL(openDoc);
    }

    setPdfProgress(100);
    setOpenDoc(url);
  } catch (err) {
    console.error("Error opening PDF:", err);
    setLoadingPdf(false);
  }
};

  useEffect(() => {
    return () => {
      if (openDoc) URL.revokeObjectURL(openDoc);
    };
  }, [openDoc]);

  const handleDragEnd = (result) => {
    if (!result.destination) return;

    const items = Array.from(clipboardItems);
    const [moved] = items.splice(result.source.index, 1);
    items.splice(result.destination.index, 0, moved);

    setClipboardItems(items);
  };

  if (loading) return <p>Loading manuals...</p>;

  return (
    <PageWrapper>
      <div className="manualsContainerLeft">
        <div className="div-header">
          <NavLink className="card-header1" to={'/dashboard/manuals'}>
            All Documents
          </NavLink>
          <NavLink className="card-header2 active" to={'/dashboard/clipboard'}>
            Clipboard
          </NavLink>
        </div>

        <DragDropContext onDragEnd={handleDragEnd}>
          <Droppable droppableId="clipboard">
            {(provided) => (
              <div
                {...provided.droppableProps}
                ref={provided.innerRef}
              >
                {clipboardItems.map((manual, index) => (
                  <Draggable
                    key={manual.id}
                    draggableId={String(manual.id)}
                    index={index}
                  >
                    {(provided) => (
                      <div
                        ref={provided.innerRef}
                        {...provided.draggableProps}
                        {...provided.dragHandleProps}
                        className="headersForManuals"
                        style={{
                          display: "flex",
                          justifyContent: "space-between",
                          alignItems: "center",
                          cursor: "grab",
                          ...provided.draggableProps.style
                        }}
                      >
                        <span
                          style={{
                            flex: 1,
                            fontSize: "15px",
                            fontWeight: "500",
                          }}
                          onClick={() => openManual(manual)}
                        >
                          {manual.title}
                        </span>

                        <div style={{ position: 'absolute', right: '20px' }}>
                          <img
                            src={bookmarkRemoveIcon}
                            alt="remove bookmark"
                            style={{ width: "24px", cursor: "pointer" }}
                            onClick={(e) => {
                              e.stopPropagation();
                              toggleClipboardItem(manual);
                              setOpenDoc(null);
                            }}
                          />
                        </div>
                      </div>
                    )}
                  </Draggable>
                ))}

                {provided.placeholder}
              </div>
            )}
          </Droppable>
        </DragDropContext>

      </div>

      <div className="manualPreviewContainer">
        <div
  style={{
    width: "100%",
    height: "83vh",
    position: "relative",
  }}
>
          {loadingPdf && (
  <div
    style={{
      position: "absolute",
      inset: 0,
      background: "var(--card)",
      zIndex: 100,
      display: "flex",
      flexDirection: "column",
      justifyContent: "center",
      alignItems: "center",
      gap: "18px",
    }}
  >
    <LoaderCircle
      size={42}
      className="manualLoader"
      color="var(--accent)"
    />

    <div
      style={{
        width: "320px",
        maxWidth: "80%",
        height: "8px",
        background: "var(--card-border)",
        borderRadius: "999px",
        overflow: "hidden",
      }}
    >
      <div
        style={{
          width: `${pdfProgress}%`,
          height: "100%",
          background: "var(--accent)",
          transition: "width .25s ease",
        }}
      />
    </div>

    <span
      style={{
        color: "var(--text)",
        fontSize: "14px",
        fontWeight: 500,
      }}
    >
      Loading manual... {pdfProgress}%
    </span>
  </div>
)}
          {openDoc ? (
            <iframe
  src={openDoc}
  width="100%"
  height="100%"
  style={{ border: "none" }}
  title="PDF preview"
  onLoad={() => {
    setPdfProgress(100);

    setTimeout(() => {
      setLoadingPdf(false);
    }, 200);
  }}
/>
          ) : (
            <p style={{ padding: "20px" }}>Select a bookmarked document to preview</p>
          )}
        </div>
      </div>
    </PageWrapper>
  );
};

export default Clipboard;
