// import React, { createContext, useState, useContext } from 'react';

// export const BookmarkContext = createContext();


// export const BookmarkProvider = ({ children }) => {
//   const [showBookmarkText, setShowBookmarkText] = useState(false);
//   const [showSOPInClipboard, setShowSOPInClipboard] = useState(false);

  
//   const toggleBookmarkText = () => {
//     setShowBookmarkText(prev => !prev);
//   };

  
//   const toggleSOPInClipboard = () => {
//     setShowSOPInClipboard(prev => !prev);
//   };

//   return (
//     <BookmarkContext.Provider value={{ showBookmarkText, toggleBookmarkText, showSOPInClipboard, toggleSOPInClipboard }}>
//       {children}
//     </BookmarkContext.Provider>
//   );
// };


// export const useBookmark = () => {
//   const context = useContext(BookmarkContext);
//   if (context === undefined) {
//     throw new Error('useBookmark must be used within a BookmarkProvider');
//   }
//   return context;
// };

import React, { createContext, useState, useContext } from 'react';


const bookmarkAddIcon = '/assets/icons/bookmarkadd.svg';
const bookmarkRemoveIcon = '/assets/icons/bookmark-remove.svg';

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
  

  
  const [showASRInClipboard, setShowASRInClipboard] = useState(false); 

  
  const toggleASRInClipboard = () => {
    setShowASRInClipboard(prev => !prev);
  };
  

  
  const [isBookmarkActive, setIsBookmarkActive] = useState(false);
  const [currentBookmarkIcon, setCurrentBookmarkIcon] = useState(bookmarkAddIcon);

  
  const handleBookmarkIconToggle = () => {
    setIsBookmarkActive(prev => {
      const newState = !prev;
      
      setCurrentBookmarkIcon(newState ? bookmarkRemoveIcon : bookmarkAddIcon);
      return newState;
    });
  };
  

  
  const manageASRAndBookmarkState = () => {
    toggleASRInClipboard();
    handleBookmarkIconToggle();
  };

  return (
    <BookmarkContext.Provider value={{
      
      showBookmarkText,
      toggleBookmarkText,
      showSOPInClipboard,
      toggleSOPInClipboard,
      
      showASRInClipboard,
      toggleASRInClipboard,
      isBookmarkActive,    
      currentBookmarkIcon, 
      handleBookmarkIconToggle,
      manageASRAndBookmarkState
    }}>
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
