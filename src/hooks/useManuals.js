import { useEffect, useState } from "react";
import { getManuals } from "../services/apiService";

export const useManuals = (categoryId = null) => {
  const [manuals, setManuals] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchManuals = async () => {
      setLoading(true);

      try {
        const params = {};

        if (categoryId) {
          params.category_id = Number(categoryId);
          params.include_descendants = true;
        }

        const data = await getManuals(params);
        setManuals(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchManuals();
  }, [categoryId]);

  return { manuals, setManuals, loading };
};
