import { useEffect, useState } from "react";
import { getManuals } from "../services/apiService";

export const useManuals = () => {
  const [manuals, setManuals] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchManuals = async () => {
      try {
        const data = await getManuals();
        setManuals(data);
      } catch (error) {
        console.error(error);
      } finally {
        setLoading(false);
      }
    };

    fetchManuals();
  }, []);

  return { manuals, loading, setManuals };
};
