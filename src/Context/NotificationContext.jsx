import React, { createContext, useContext, useEffect, useState } from "react";
import { getManualUpdates } from "../services/apiService";
import { useAuth } from "../auth/useAuth";

const NotificationContext = createContext();

export const useNotifications = () => useContext(NotificationContext);

export const NotificationProvider = ({ children }) => {
  const { user } = useAuth();

  const [updates, setUpdates] = useState([]);
  const [seenIds, setSeenIds] = useState([]);
  const [updateCount, setUpdateCount] = useState(0);
  const [loading, setLoading] = useState(false);

  const storageKey = user ? `manualUpdatesSeen_${user.id}` : null;

  const loadSeen = () => {
    if (!storageKey) return [];
    const data = localStorage.getItem(storageKey);
    return data ? JSON.parse(data) : [];
  };

  const saveSeen = (ids) => {
    if (!storageKey) return;
    localStorage.setItem(storageKey, JSON.stringify(ids));
  };

  const calculateUnread = (items, seen) => {
    return items.filter((u) => !seen.includes(String(u.id))).length;
  };

  const refreshUpdates = async () => {
    if (!user) return;

    try {
      setLoading(true);

      const data = await getManualUpdates();
      const items = data?.items || data?.results || data?.data || [];

      const seen = loadSeen();

      setUpdates(items);
      setSeenIds(seen);
      setUpdateCount(calculateUnread(items, seen));
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refreshUpdates();

    const interval = setInterval(refreshUpdates, 30000);

    return () => clearInterval(interval);
  }, [user]);

  const markAsSeen = (id) => {
    const idStr = String(id);

    if (seenIds.includes(idStr)) return;

    const newSeen = [...seenIds, idStr];

    setSeenIds(newSeen);
    saveSeen(newSeen);

    setUpdateCount(calculateUnread(updates, newSeen));
  };

  return (
    <NotificationContext.Provider
      value={{
        updates,
        seenIds,
        updateCount,
        loading,
        markAsSeen,
      }}
    >
      {children}
    </NotificationContext.Provider>
  );
};
