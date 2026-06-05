import { useState } from "react";
import { deleteManual } from "../services/apiService";

export const useDeleteManual = (onDeleted) => {
  const [loading, setLoading] = useState(false);

  const handleDelete = async (manualId, note) => {
    try {
      setLoading(true);

      await deleteManual(manualId, note);

      if (onDeleted) onDeleted(manualId);
    } catch (error) {
      console.error("Delete failed:", error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  return { loading, handleDelete };
};
