import React, { createContext, useState, useContext } from 'react';

export const BookmarkContext = createContext();


export const BookmarkProvider = ({ children }) => {
  const [showBookmarkText, setShowBookmarkText] = useState(false);
  const [showSOPInClipboard, setShowSOPInClipboard] = useState(false);

  
  const toggleBookmarkText = () => {
    setShowBookmarkText(prev => !prev);
  };

  
  const toggleSOPInClipboard = () => {
    setShowSOPInClipboard(prev => !prev);
  };

  return (
    <BookmarkContext.Provider value={{ showBookmarkText, toggleBookmarkText, showSOPInClipboard, toggleSOPInClipboard }}>
      {children}
    </BookmarkContext.Provider>
  );
};


export const useBookmark = () => {
  const context = useContext(BookmarkContext);
  if (context === undefined) {
    throw new Error('useBookmark must be used within a BookmarkProvider');
  }
  return context;
};
