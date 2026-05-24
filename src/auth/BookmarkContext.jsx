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

// تعریف مسیر آیکون‌ها (مطمئن شوید این مسیرها صحیح هستند)
const bookmarkAddIcon = '/assets/icons/bookmarkadd.svg'; // آیکون بوکمارک غیرفعال
const bookmarkRemoveIcon = '/assets/icons/bookmark-remove.svg'; // آیکون بوکمارک فعال

export const BookmarkContext = createContext();

export const BookmarkProvider = ({ children }) => {
  // --- قابلیت‌های موجود ---
  const [showBookmarkText, setShowBookmarkText] = useState(false); // برای متن عمومی
  const [showSOPInClipboard, setShowSOPInClipboard] = useState(false); // برای نمایش SOP

  const toggleBookmarkText = () => {
    setShowBookmarkText(prev => !prev);
  };

  const toggleSOPInClipboard = () => {
    setShowSOPInClipboard(prev => !prev);
  };
  // --- پایان قابلیت‌های موجود ---

  // --- قابلیت‌های جدید برای ASR ---
  const [showASRInClipboard, setShowASRInClipboard] = useState(false); // وضعیت نمایش ASR

  // تابعی برای تغییر وضعیت نمایش ASR
  const toggleASRInClipboard = () => {
    setShowASRInClipboard(prev => !prev);
  };
  // --- پایان قابلیت‌های جدید برای ASR ---

  // --- قابلیت‌های جدید برای مدیریت آیکون بوکمارک ---
  const [isBookmarkActive, setIsBookmarkActive] = useState(false); // وضعیت فعال بودن آیکون
  const [currentBookmarkIcon, setCurrentBookmarkIcon] = useState(bookmarkAddIcon); // آیکون فعلی

  // تابعی برای مدیریت کلیک روی آیکون بوکمارک (تغییر وضعیت و آیکون)
  const handleBookmarkIconToggle = () => {
    setIsBookmarkActive(prev => {
      const newState = !prev;
      // تغییر تصویر آیکون بر اساس وضعیت جدید
      setCurrentBookmarkIcon(newState ? bookmarkRemoveIcon : bookmarkAddIcon);
      return newState;
    });
  };
  // --- پایان قابلیت‌های جدید برای آیکون بوکمارک ---

  // --- تابع ترکیبی برای مدیریت ASR و آیکون بوکمارک (هنگام کلیک روی ASR) ---
  // این تابع هم ASR را toggle می‌کند و هم وضعیت آیکون بوکمارک را تغییر می‌دهد.
  const manageASRAndBookmarkState = () => {
    toggleASRInClipboard();      // وضعیت نمایش ASR را تغییر می‌دهد
    handleBookmarkIconToggle(); // وضعیت آیکون بوکمارک را تغییر می‌دهد
  };

  return (
    <BookmarkContext.Provider value={{
      // --- مقادیر موجود ---
      showBookmarkText,
      toggleBookmarkText,
      showSOPInClipboard,
      toggleSOPInClipboard,
      // --- مقادیر جدید ---
      showASRInClipboard,       // وضعیت نمایش ASR
      toggleASRInClipboard,     // تابع toggle برای ASR
      isBookmarkActive,         // وضعیت فعال بودن آیکون بوکمارک
      currentBookmarkIcon,      // آیکون فعلی بوکمارک
      handleBookmarkIconToggle, // تابع برای تغییر آیکون بوکمارک
      manageASRAndBookmarkState // تابع ترکیبی برای مدیریت ASR و آیکون بوکمارک
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
