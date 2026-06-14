import React, { createContext, useContext, useState, useEffect } from "react";
import { useAuth } from "../auth/useAuth";

export const BookmarkContext = createContext();

export const BookmarkProvider = ({ children }) => {
  const { user } = useAuth();

  const storageKey = user ? `clipboard_${user.id}` : "clipboard_guest";

  const [clipboardItems, setClipboardItems] = useState([]);


  useEffect(() => {
    const saved = localStorage.getItem(storageKey);
    setClipboardItems(saved ? JSON.parse(saved) : []);
  }, [storageKey]);


  useEffect(() => {
    localStorage.setItem(storageKey, JSON.stringify(clipboardItems));
  }, [clipboardItems, storageKey]);

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
        setClipboardItems,
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
