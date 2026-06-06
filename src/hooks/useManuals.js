import { useEffect, useState } from "react";
import { getManuals } from "../services/apiService";

export const useManuals = (categoryId = null) => {
  const [manuals, setManuals] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchManuals = async () => {
      setLoading(true);
      try {
        const data = await getManuals({
          category_id: categoryId,
          include_descendants: true,
        });

        setManuals(data);
      } catch (error) {
        console.error(error);
      } finally {
        setLoading(false);
      }
    };

    fetchManuals();
  }, [categoryId]);

  return { manuals, loading };
};
