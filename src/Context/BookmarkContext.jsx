import React, { createContext, useContext, useState, useEffect } from "react";

export const BookmarkContext = createContext();

export const BookmarkProvider = ({ children }) => {

  const [clipboardItems, setClipboardItems] = useState(() => {
    const saved = localStorage.getItem("clipboardItems");
    return saved ? JSON.parse(saved) : [];
  });

  useEffect(() => {
    localStorage.setItem("clipboardItems", JSON.stringify(clipboardItems));
  }, [clipboardItems]);

  const toggleClipboardItem = (doc) => {
    setClipboardItems((prev) => {
      const exists = prev.find((item) => item.id === doc.id);

      if (exists) {
        return prev.filter((item) => item.id !== doc.id);
      }

      return [...prev, doc];
    });
  };

  const isDocumentBookmarked = (id) => {
    return clipboardItems.some((item) => item.id === id);
  };

  return (
    <BookmarkContext.Provider
      value={{
        clipboardItems,
        toggleClipboardItem,
        isDocumentBookmarked
      }}
    >
      {children}
    </BookmarkContext.Provider>
  );
};

export const useBookmark = () => {
  return useContext(BookmarkContext);
};
