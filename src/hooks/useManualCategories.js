// import { useEffect, useState } from "react";
// import { getManualCategoryTree } from "../services/apiService";

// export const useManualCategories = (parentId = null) => {
//   const [categories, setCategories] = useState([]);
//   const [fullTree, setFullTree] = useState([]);
//   const [loading, setLoading] = useState(true);

//   useEffect(() => {
//     const loadCategories = async () => {
//       try {
//         const data = await getManualCategoryTree();
//         setFullTree(data);

//         if (parentId) {
//           const parentNode = findNodeById(data, Number(parentId));
//           setCategories(parentNode?.children || []);
//         } else {
//           setCategories(data);
//         }
//       } catch (err) {
//         console.error("Failed to load categories", err);
//       } finally {
//         setLoading(false);
//       }
//     };
//     loadCategories();
//   }, [parentId]);

//   const findNodeById = (nodes, id) => {
//     for (const node of nodes) {
//       if (node.id === id) return node;
//       if (node.children) {
//         const childMatch = findNodeById(node.children, id);
//         if (childMatch) return childMatch;
//       }
//     }
//     return null;
//   };

//   return { categories, fullTree, loading };
// };

import { useEffect, useState } from "react";
import { getManualCategoryTree } from "../services/apiService";

export const useManualCategories = (parentId = null) => {
  const [categories, setCategories] = useState([]);
  const [currentCategory, setCurrentCategory] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadCategories = async () => {
      setLoading(true);
      try {
        const data = await getManualCategoryTree();
        if (parentId) {
          const findNode = (nodes, id) => {
            for (const node of nodes) {
              if (String(node.id) === String(id)) return node;
              if (node.children) {
                const match = findNode(node.children, id);
                if (match) return match;
              }
            }
            return null;
          };
          const node = findNode(data, parentId);
          setCategories(node?.children || []);
          setCurrentCategory(node);
        } else {
          setCategories(data);
          setCurrentCategory(null);
        }
      } catch (err) {
        console.error("Failed to load categories", err);
      } finally {
        setLoading(false);
      }
    };
    loadCategories();
  }, [parentId]);

  return { categories, currentCategory, loading };
};
