// import React, { createContext, useContext, useEffect, useState } from "react";
// import { getManualUpdates } from "../services/apiService";
// import { useAuth } from "../auth/useAuth";

// const NotificationContext = createContext();

// export const useNotifications = () => useContext(NotificationContext);

// export const NotificationProvider = ({ children }) => {
//   const { user } = useAuth();

//   const [updates, setUpdates] = useState([]);
//   const [seenIds, setSeenIds] = useState([]);
//   const [updateCount, setUpdateCount] = useState(0);
//   const [loading, setLoading] = useState(false);

//   const storageKey = user ? `manualUpdatesSeen_${user.id}` : null;

//   const loadSeen = () => {
//     if (!storageKey) return [];
//     const data = localStorage.getItem(storageKey);
//     return data ? JSON.parse(data) : [];
//   };

//   const saveSeen = (ids) => {
//     if (!storageKey) return;
//     localStorage.setItem(storageKey, JSON.stringify(ids));
//   };

//   const calculateUnread = (items, seen) => {
//     return items.filter((u) => !seen.includes(String(u.id))).length;
//   };

//   const refreshUpdates = async () => {
//     if (!user) return;

//     try {
//       setLoading(true);

//       const data = await getManualUpdates();
//       const items = data?.items || data?.results || data?.data || [];

//       const seen = loadSeen();

//       setUpdates(items);
//       setSeenIds(seen);
//       setUpdateCount(calculateUnread(items, seen));
//     } catch (err) {
//       console.error(err);
//     } finally {
//       setLoading(false);
//     }
//   };

//   useEffect(() => {
//     refreshUpdates();

//     const interval = setInterval(refreshUpdates, 10000);

//     return () => clearInterval(interval);
//   }, [user]);

//   const markAsSeen = (id) => {
//     const idStr = String(id);

//     if (seenIds.includes(idStr)) return;

//     const newSeen = [...seenIds, idStr];

//     setSeenIds(newSeen);
//     saveSeen(newSeen);

//     setUpdateCount(calculateUnread(updates, newSeen));
//   };
// const markAllAsSeen = () => {
//   if (!updates.length) return;

//   const allIds = updates.map((u) => String(u.id));

//   setSeenIds(allIds);
//   saveSeen(allIds);
//   setUpdateCount(0);
// };
//   return (
//     <NotificationContext.Provider
//       value={{
//         updates,
//         seenIds,
//         updateCount,
//         loading,
//         markAsSeen,
//         markAllAsSeen,
//         refreshUpdates
//       }}
//     >
//       {children}
//     </NotificationContext.Provider>
//   );
// };
import React, { createContext, useContext, useEffect, useState } from "react";
import {
  getManualUpdates,
  markManualUpdateRead,
  markAllManualUpdatesRead,
} from "../services/apiService";
import { useAuth } from "../auth/useAuth";

const NotificationContext = createContext();

export const useNotifications = () => useContext(NotificationContext);

export const NotificationProvider = ({ children }) => {
  const { user } = useAuth();

  const [updates, setUpdates] = useState([]);
  const [seenIds, setSeenIds] = useState([]);
  const [updateCount, setUpdateCount] = useState(0);
  const [loading, setLoading] = useState(false);

  const refreshUpdates = async () => {
    if (!user) return;

    try {
      setLoading(true);

      const data = await getManualUpdates();
      const items = data?.items || data?.results || data?.data || [];

      
      const seen = items
        .filter((u) => u.is_read)
        .map((u) => String(u.id));

      setUpdates(items);
      setSeenIds(seen);
      setUpdateCount(items.length - seen.length);
    } catch (err) {
      console.error("refreshUpdates error:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refreshUpdates();

    const interval = setInterval(refreshUpdates, 30000);

    return () => clearInterval(interval);
  }, [user]);

  const markAsSeen = async (id) => {
    const idStr = String(id);

    if (seenIds.includes(idStr)) return;

    try {
      await markManualUpdateRead(id);

      
      const newSeen = [...seenIds, idStr];
      setSeenIds(newSeen);
      setUpdateCount(updates.length - newSeen.length);
    } catch (err) {
      console.error("markAsSeen error:", err);
    }
  };

  const markAllAsSeen = async () => {
    if (!updates.length) return;

    try {
      await markAllManualUpdatesRead();

      const allIds = updates.map((u) => String(u.id));

      setSeenIds(allIds);
      setUpdateCount(0);
    } catch (err) {
      console.error("markAllAsSeen error:", err);
    }
  };

  return (
    <NotificationContext.Provider
      value={{
        updates,
        seenIds,
        updateCount,
        loading,
        markAsSeen,
        markAllAsSeen,
        refreshUpdates,
      }}
    >
      {children}
    </NotificationContext.Provider>
  );
};
