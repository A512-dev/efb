
// import { useParams, NavLink } from "react-router-dom";
// import { useState, useEffect } from "react";
// import { useManuals } from "../hooks/useManuals";

// import { useManualCategories } from "../hooks/useManualCategories";
// import { useBookmark } from "../Context/BookmarkContext";
// import PageWrapper from "../components/PageWrapper";
// import { downloadManual } from "../services/apiService";


// import bookmarkAddIcon from "../assets/icons/bookmarkadd.svg";
// import bookmarkRemoveIcon from "../assets/icons/bookmarkpor.svg";

// const Manuals = () => {
//   const { categoryId } = useParams();

//   const { categories, loading: categoriesLoading } =
//     useManualCategories(categoryId || null);

//   const isLeafCategory = !categories || categories.length === 0;

//   const { manuals, loading } = useManuals(
//     isLeafCategory ? categoryId || null : null
//   );

  
//   const { toggleClipboardItem, isDocumentBookmarked } = useBookmark();

//   const [openDoc, setOpenDoc] = useState(null);

//   const openManual = async (manual) => {
//     try {
//       const blob = await downloadManual(manual.id);
//       const url = URL.createObjectURL(blob);
//       setOpenDoc(url);
//     } catch (err) {
//       console.error("Error opening PDF:", err);
//     }
//   };

//   useEffect(() => {
//     if (!isLeafCategory) {
//       setOpenDoc(null);
//     }
//   }, [isLeafCategory, categoryId]);

//   useEffect(() => {
//     return () => {
//       if (openDoc) URL.revokeObjectURL(openDoc);
//     };
//   }, [openDoc]);

//   if (categoriesLoading) return <p>Loading...</p>;
//   if (isLeafCategory && loading) return <p>Loading manuals...</p>;

//   return (
//     <PageWrapper>
//       <div className="manualsContainerLeft">
//         <div className="div-header">
//           <NavLink className="card-header1" to="/dashboard/manuals">
//             All Documents
//           </NavLink>

//           <NavLink className="card-header2" to="/dashboard/clipboard">
//             Clipboard
//           </NavLink>
//         </div>

//         {!isLeafCategory &&
//           categories.map((category) => (
//             <NavLink
//               key={category.id}
//               className="headersForManuals"
//               to={`/dashboard/category/${category.id}`}
//             >
//               {category.name}
//             </NavLink>
//           ))}

//         {isLeafCategory &&
//           manuals.map((manual) => (
//             <div
//               key={manual.id}
//               className="headersForManuals"
//               style={{
//                 display: "flex",
//                 justifyContent: "space-between",
//                 alignItems: "center",
//               }}
//             >
//               <span
//                 style={{
//                   cursor: "pointer",
//                   fontSize: "15px",
//                   fontWeight: "500",
//                 }}
//                 onClick={() => openManual(manual)}
//               >
//                 {manual.title}
//               </span>

//               <div style={{ display: "flex", gap: "2px",position:'absolute',right:'20px' }}>
//                 <img
//                   src={
//                     isDocumentBookmarked(manual.id)
//                       ? bookmarkRemoveIcon
//                       : bookmarkAddIcon
//                   }
//                   alt="bookmark"
//                   style={{ width: "24px", cursor: "pointer" }}
//                   onClick={() => toggleClipboardItem(manual)}
//                 />

                
//               </div>
//             </div>
//           ))}
//       </div>

//       {isLeafCategory && (
//         <div className="manualsContainer">
//           <div style={{ width: "100%", height: "100vh" }}>
//             {openDoc ? (
//               <iframe
//                 src={openDoc}
//                 width="100%"
//                 height="100%"
//                 style={{ border: "none" }}
//                 title="PDF preview"
//               />
//             ) : (
//               <p style={{ padding: "20px" }}>Select a document to preview</p>
//             )}
//           </div>
//         </div>
//       )}
//     </PageWrapper>
//   );
// };

// export default Manuals;

import { useParams, NavLink } from "react-router-dom";
import { useState, useEffect } from "react";
import { useManuals } from "../hooks/useManuals";
import { useManualCategories } from "../hooks/useManualCategories";
import { useBookmark } from "../Context/BookmarkContext";
import PageWrapper from "../components/PageWrapper";
import { downloadManual } from "../services/apiService";

import bookmarkAddIcon from "../assets/icons/bookmarkadd.svg";
import bookmarkRemoveIcon from "../assets/icons/bookmarkpor.svg";

const Manuals = () => {
  const { categoryId } = useParams();

  const { categories, loading: categoriesLoading } =
    useManualCategories(categoryId || null);

  // --- منطق جدید برای سینک کردن با بخش ادمین ---
  const getProcessedCategories = () => {
    if (!categories) return [];
    
    const seenForms = new Set();
    const finalCategories = [];

    categories.forEach((category) => {
      // لیست اسامی که باید در هم ادغام شوند
      const specialNames = ["REPORTS", "sms", "training"];
      
      if (specialNames.includes(category.name)) {
        if (!seenForms.has("Forms")) {
          finalCategories.push({ ...category, name: "Forms" });
          seenForms.add("Forms");
        }
      } else {
        finalCategories.push(category);
      }
    });

    return finalCategories;
  };

  const displayCategories = getProcessedCategories();
  // --------------------------------------------

  const isLeafCategory = !categories || categories.length === 0;

  const { manuals, loading } = useManuals(
    isLeafCategory ? categoryId || null : null
  );

  const { toggleClipboardItem, isDocumentBookmarked } = useBookmark();
  const [openDoc, setOpenDoc] = useState(null);

  const openManual = async (manual) => {
    try {
      const blob = await downloadManual(manual.id);
      const url = URL.createObjectURL(blob);
      setOpenDoc(url);
    } catch (err) {
      console.error("Error opening PDF:", err);
    }
  };

  useEffect(() => {
    if (!isLeafCategory) {
      setOpenDoc(null);
    }
  }, [isLeafCategory, categoryId]);

  useEffect(() => {
    return () => {
      if (openDoc) URL.revokeObjectURL(openDoc);
    };
  }, [openDoc]);

  if (categoriesLoading) return <p>Loading...</p>;
  if (isLeafCategory && loading) return <p>Loading manuals...</p>;

  return (
    <PageWrapper>
      <div className="manualsContainerLeft">
        <div className="div-header">
          <NavLink className="card-header1" to="/dashboard/manuals">
            All Documents
          </NavLink>

          <NavLink className="card-header2" to="/dashboard/clipboard">
            Clipboard
          </NavLink>
        </div>

        {!isLeafCategory &&
          displayCategories.map((category) => (
            <NavLink
              key={category.id}
              className="headersForManuals"
              to={`/dashboard/category/${category.id}`}
            >
              {category.name}
            </NavLink>
          ))}

        {isLeafCategory &&
          manuals.map((manual) => (
            <div
              key={manual.id}
              className="headersForManuals"
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
              }}
            >
              <span
                style={{
                  cursor: "pointer",
                  fontSize: "15px",
                  fontWeight: "500",
                }}
                onClick={() => openManual(manual)}
              >
                {manual.title}
              </span>

              <div style={{ display: "flex", gap: "2px", position: 'absolute', right: '20px' }}>
                <img
                  src={
                    isDocumentBookmarked(manual.id)
                      ? bookmarkRemoveIcon
                      : bookmarkAddIcon
                  }
                  alt="bookmark"
                  style={{ width: "24px", cursor: "pointer" }}
                  onClick={() => toggleClipboardItem(manual)}
                />
              </div>
            </div>
          ))}
      </div>

      {isLeafCategory && (
        <div className="manualsContainer">
          <div style={{ width: "100%", height: "100vh" }}>
            {openDoc ? (
              <iframe
                src={openDoc}
                width="100%"
                height="100%"
                style={{ border: "none" }}
                title="PDF preview"
              />
            ) : (
              <p style={{ padding: "20px" }}>Select a document to preview</p>
            )}
          </div>
        </div>
      )}
    </PageWrapper>
  );
};

export default Manuals;
