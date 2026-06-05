import React, { createContext, useContext, useState, useEffect } from "react";

const bookmarkAddIcon = "/assets/icons/bookmarkadd.svg";
const bookmarkRemoveIcon = "/assets/icons/bookmark-remove.svg";

export const BookmarkContext = createContext();

export const BookmarkProvider = ({ children }) => {

  const [clipboardItems, setClipboardItems] = useState(() => {
    const saved = localStorage.getItem("clipboardItems");
    return saved ? JSON.parse(saved) : [];
  });

  const [isBookmarkActive, setIsBookmarkActive] = useState(false);
  const [currentBookmarkIcon, setCurrentBookmarkIcon] = useState(bookmarkAddIcon);

  const [showDoc, setShowDoc] = useState(null);

  useEffect(() => {
    localStorage.setItem("clipboardItems", JSON.stringify(clipboardItems));
  }, [clipboardItems]);

  const toggleClipboardItem = (doc) => {
    setClipboardItems((prev) => {
      const exists = prev.find((item) => item.title === doc.title);

      if (exists) {
        return prev.filter((item) => item.title !== doc.title);
      }

      return [...prev, doc];
    });
  };

  const isDocumentBookmarked = (title) => {
    return clipboardItems.some((item) => item.title === title);
  };

  const handleBookmarkIconToggle = (doc) => {
    toggleClipboardItem(doc);

    const active = !isDocumentBookmarked(doc.title);

    setIsBookmarkActive(active);
    setCurrentBookmarkIcon(active ? bookmarkRemoveIcon : bookmarkAddIcon);
  };

  return (
    <BookmarkContext.Provider
      value={{
        clipboardItems,
        toggleClipboardItem,
        isDocumentBookmarked,
        handleBookmarkIconToggle,
        currentBookmarkIcon,
        showDoc,
        setShowDoc
      }}
    >
      {children}
    </BookmarkContext.Provider>
  );
};

export const useBookmark = () => {
  return useContext(BookmarkContext);
};
