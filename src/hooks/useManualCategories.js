import { useEffect, useState } from "react";
import { getManualCategoryTree } from "../services/apiService";

export const useManualCategories = (parentId = null) => {
  const [categories, setCategories] = useState([]);
  const [fullTree, setFullTree] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadCategories = async () => {
      try {
        const data = await getManualCategoryTree();
        setFullTree(data);

        if (parentId) {
          const parentNode = findNodeById(data, Number(parentId));
          setCategories(parentNode?.children || []);
        } else {
          setCategories(data);
        }
      } catch (err) {
        console.error("Failed to load categories", err);
      } finally {
        setLoading(false);
      }
    };
    loadCategories();
  }, [parentId]);

  const findNodeById = (nodes, id) => {
    for (const node of nodes) {
      if (node.id === id) return node;
      if (node.children) {
        const childMatch = findNodeById(node.children, id);
        if (childMatch) return childMatch;
      }
    }
    return null;
  };

  return { categories, fullTree, loading };
};
