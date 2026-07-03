
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
  import backIcon from '../assets/icons/arrowback .svg'
  import bookmarkAddIcon from "../assets/icons/bookmarkadd.svg";
  import bookmarkRemoveIcon from "../assets/icons/bookmarkpor.svg";
  import { useNotifications } from "../Context/NotificationContext";
  import PDFViewer from "../components/manuals/PDFViewer";
  import { getMyManualReads } from "../services/apiService";
  import { markManualRead } from "../services/apiService";
  import { getCurrentUser } from "../services/apiService";
  import { useDownloadManual } from "../hooks/useDownloadManual";
import { useDeleteManual } from "../hooks/useDeleteManual";
import {
  uploadManual,
  getManualCategoryTree,
} from "../services/apiService";
import { LoaderCircle } from "lucide-react";
import {
  EllipsisVertical,
  Download,
  Trash2,
  FilePenLine,
} from "lucide-react";
import {
  updateManualPdf,
} from "../services/apiService";
  const Manuals = () => {
    const { categoryId } = useParams();

    const { categories, currentCategory, loading: categoriesLoading } = useManualCategories(categoryId || null);
  const { updates, seenIds } = useNotifications();
  const [hideReadCheckbox, setHideReadCheckbox] = useState({});
const [updatingId, setUpdatingId] = useState(null);
  const [readManuals, setReadManuals] = useState([]);
  const [unreadUserManuals, setUnreadUserManuals] = useState([]);
  const isLeafCategory = !categories || categories.length === 0;
  const [title, setTitle] = useState("");
const [file, setFile] = useState(null);
const [uploadCategoryId, setUploadCategoryId] = useState("");
const [uploading, setUploading] = useState(false);
  const { manuals,setManuals, loading } = useManuals(
      isLeafCategory ? categoryId || null : null
    );
  const [currentUser, setCurrentUser] = useState(null);
const [openMenuId, setOpenMenuId] = useState(null);
const [openDoc, setOpenDoc] = useState(null);
const [loadingPdf, setLoadingPdf] = useState(false);
const [pdfProgress, setPdfProgress] = useState(10);
const { handleDownload } = useDownloadManual();
const [uploadCategories, setUploadCategories] = useState([]);

useEffect(() => {
  getManualCategoryTree().then(setUploadCategories);
}, []);
const handleUpload = async (e) => {
  e.preventDefault();

  if (!title.trim()) {
    alert("Title is required");
    return;
  }

  if (!file) {
    alert("Please select a PDF");
    return;
  }

  if (!uploadCategoryId) {
    alert("Select a category");
    return;
  }

  try {
    setUploading(true);

    const note =
      window.prompt("Note for this upload (optional):", "") ?? "";

    const newManual = await uploadManual(
      file,
      title.trim(),
      note,
      Number(uploadCategoryId)
    );

    setManuals((prev) => [newManual, ...prev]);

    setTitle("");
    setFile(null);
    setUploadCategoryId("");

    alert("Uploaded successfully");
  } catch (err) {
    console.error(err);
    alert("Upload failed");
  } finally {
    setUploading(false);
  }
};
const handleReplace = async (manual, e) => {
  const newFile = e.target.files?.[0];
  if (!newFile) return;

  if (!window.confirm(`Replace PDF for "${manual.title}"?`)) return;

  try {
    setUpdatingId(manual.id);

    const updated = await updateManualPdf(manual.id, newFile, {
      title: manual.title,
    });

    setManuals((prev) =>
      prev.map((m) =>
        m.id === manual.id ? { ...m, ...updated } : m
      )
    );
setSelectedManual((prev) =>
  prev?.id === manual.id
    ? { ...prev, ...updated }
    : prev
);
    alert("Updated successfully");
  } catch (err) {
    alert("Update failed");
  } finally {
    setUpdatingId(null);
  }
};
const flattenCategories = (nodes, prefix = "") => {
  let result = [];

  nodes.forEach((node) => {
    const label = prefix ? `${prefix} > ${node.name}` : node.name;

    if (!node.children?.length) {
      result.push({
        id: node.id,
        label,
      });
    }

    if (node.children?.length) {
      result = result.concat(
        flattenCategories(node.children, label)
      );
    }
  });

  return result;
};
const categoryOptions = flattenCategories(uploadCategories);
const handleDeleteClick = async (manual) => {
  if (!window.confirm(`Delete "${manual.title}"?`)) return;

  const note = window.prompt("Reason:", "") ?? "";

  try {
    await handleDelete(manual.id, note);
    alert("Deleted");
  } catch {
    alert("Delete failed");
  }
};
const { handleDelete } = useDeleteManual((manualId) => {
  setManuals((prev) => prev.filter((m) => m.id !== manualId));
});
useEffect(() => {
  const closeMenu = () => setOpenMenuId(null);

  window.addEventListener("click", closeMenu);

  return () => {
    window.removeEventListener("click", closeMenu);
  };
}, []);
useEffect(() => {
  getCurrentUser().then(setCurrentUser);
}, []);

const isAdmin = currentUser?.role === "admin";
  useEffect(() => {
    const fetchReads = async () => {
      try {
        const data = await getMyManualReads();
        const items = Array.isArray(data) ? data : data?.items || [];
        const ids = items.map((item) => item.manual_id);

        setReadManuals(ids);
      } catch (err) {
        console.error("Error fetching read manuals", err);
      }
    };

    fetchReads();
  }, []);
  useEffect(() => {
    const loadUnreadManuals = async () => {
      try {
        const data = await getMyManualReads();

        const readItems = Array.isArray(data)
          ? data
          : data?.items || [];

        const readIds = readItems.map(
          (item) => String(item.manual_id || item.manualId)
        );

        const unread = manuals.filter(
          (manual) => !readIds.includes(String(manual.id))
        );

        setUnreadUserManuals(unread);

      } catch (err) {
        console.error("Failed to load unread manuals:", err);
      }
    };

    if (manuals.length > 0) {
      loadUnreadManuals();
    }
  }, [manuals]);

  const handleRead = async (manualId) => {
    try {
      if (readManuals.includes(manualId)) return;

      await markManualRead(manualId);

      setReadManuals((prev) =>
        prev.includes(manualId) ? prev : [...prev, manualId]
      );

      
      setTimeout(() => {
        setHideReadCheckbox((prev) => ({
          ...prev,
          [manualId]: true,
        }));
      }, 5000);

    } catch (err) {
      console.error("Error marking manual as read", err);
    }
  };



  const getProcessedCategories = () => {
    if (!categories) return [];
    
    const seenForms = new Set();
    const finalCategories = [];

    const isInsideIranAir = currentCategory?.name === "Iranair";
    const isInsideTraining = currentCategory?.name === "Training and resources";

    
    if (isInsideIranAir) {
      if (categories.length > 0) {
        finalCategories.push({
          ...categories[0],
          name: "Company Manuals"
        });
      }
      return finalCategories;
    }

    
    if (isInsideTraining) {

      const firstChild = categories[0];
      const secondChild = categories[1];

      if (firstChild) {
        finalCategories.push({
          ...firstChild,
          name: "Dgr"
        });
      }

      if (secondChild) {
        finalCategories.push({
          ...secondChild,
          name: "lcao"
        });
      }

      return finalCategories;
    }


    categories.forEach((category) => {

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
    

    

    
const hiddenManualIds = new Set(
  updates
    .filter((item) => {
      if (isAdmin) return false; 
      return !seenIds.includes(String(item.id));
    })
    .map((item) => String(item.manual_id))
);

const visibleManuals = manuals.filter(
  (manual) => !hiddenManualIds.has(String(manual.id))
);


    const { toggleClipboardItem, isDocumentBookmarked } = useBookmark();
    const [selectedManual, setSelectedManual] = useState(null);


  // const openManual = (manual) => {
  //   console.log("Clicked manual:", manual);
  //   setSelectedManual(manual);
  // };  
const openManual = async (manual) => {
  try {
    setLoadingPdf(true);
    setPdfProgress(10);

    const timer = setInterval(() => {
      setPdfProgress((prev) => (prev < 90 ? prev + 10 : prev));
    }, 150);

    const blob = await downloadManual(manual.id);
    const url = URL.createObjectURL(blob);

    clearInterval(timer);

    if (openDoc) {
      URL.revokeObjectURL(openDoc);
    }

    setPdfProgress(100);

    setOpenDoc(url);
    setSelectedManual(manual);

  } catch (err) {
    console.error("Error opening PDF:", err);
    setLoadingPdf(false);
  }
};
useEffect(() => {
  return () => {
    if (openDoc) {
      URL.revokeObjectURL(openDoc);
    }
  };
}, [openDoc]);
    useEffect(() => {
    if (!isLeafCategory) {
      setSelectedManual(null);
    }
  }, [isLeafCategory, categoryId]);



    if (categoriesLoading) return <p>Loading...</p>;
    if (isLeafCategory && loading) return <p>Loading manuals...</p>;
  const getHeaderTitle = () => {

    if (!currentCategory) return "Documents";

    
    if (currentCategory.id === 9) {
      return "Company Manuals";
    }
    if (currentCategory.id === 15) {
      return "Training and resources";
    }

    
    if (currentCategory.id === 16) {
      return "Dgr";
    }

    
    if (currentCategory.id === 17) {
      return "lcao";
    }
  if (currentCategory.id === 23) {
      return "Forms";
    }
    return currentCategory.name;
  };



  

    return (
      <PageWrapper>
        <div className="manualsContainerLeft">
          <div className="div-header">
    
    {!categoryId ? (
      <div className="card-header1 active" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        All Documents
      </div>
    ) : (
      <NavLink 
        className="card-header1" 
        style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}
        to={currentCategory?.parent_id ? `/dashboard/category/${currentCategory.parent_id}` : "/dashboard/manuals"}
      >
        <img src={backIcon} alt="back" style={{ width: "23px" }} />
      </NavLink>
    )}

    
    {!categoryId ? (
      <NavLink className="card-header2" to="/dashboard/clipboard" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        Clipboard
      </NavLink>
    ) : (
      <div className="card-header2 active" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'default' }}>
        {getHeaderTitle()}

      </div>
    )}
  </div>



          {!isLeafCategory &&
            displayCategories.map((category) => (
              <NavLink
                key={category.id}
                className="headersForManuals" style={{textWrap:'auto'}}
                to={`/dashboard/category/${category.id}`}
              >
                {category.name}
              </NavLink>
            ))}


          {isLeafCategory &&
    visibleManuals.map((manual) => (

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
                    fontWeight: "500",textWrap:'auto'
                  }}
                  onClick={() => openManual(manual)}
                >
                  {manual.title}
                </span>
<div
  style={{
    display: "flex",
    alignItems: "center",
    gap: "8px",
    marginLeft: "auto",
    position: "relative",
  }}
>
  {isAdmin ? (
    <>
      <button
  className="manualMenuBtn"
  onClick={(e) => {
    e.stopPropagation();
    setOpenMenuId(
      openMenuId === manual.id ? null : manual.id
    );
  }}
>
  <EllipsisVertical size={18} strokeWidth={2} />
</button>

      {openMenuId === manual.id && (
        <div
          className="manualMenu"
          onClick={(e) => e.stopPropagation()}
        >
          <button
            onClick={() => {
              document
                .getElementById(`replace-${manual.id}`)
                ?.click();
              setOpenMenuId(null);
            }}
          >
            <FilePenLine size={16} />
              <span> Replace PDF</span>
          </button>

          <button
            onClick={() => {
              handleDownload(manual);
              setOpenMenuId(null);
            }}
          >
            <Download size={16} />
  <span> Download</span>
          </button>

          <button
            className="danger"
            onClick={() => {
              handleDeleteClick(manual);
              setOpenMenuId(null);
            }}
          >
            <Trash2 size={16} />
  <span> Delete</span>
          </button>
        </div>
      )}

      <input
        id={`replace-${manual.id}`}
        type="file"
        accept="application/pdf"
        style={{ display: "none" }}
        onChange={(e) => handleReplace(manual, e)}
      />
    </>
  ) : (
    !hideReadCheckbox[manual.id] && (
      <input
        type="checkbox"
        className="readAndSignButton"
        checked={readManuals.includes(manual.id)}
        disabled={
          selectedManual?.id !== manual.id ||
          readManuals.includes(manual.id)
        }
        onChange={() => handleRead(manual.id)}
      />
    )
  )}

  <img
    src={
      isDocumentBookmarked(manual.id)
        ? bookmarkRemoveIcon
        : bookmarkAddIcon
    }
    alt="bookmark"
    style={{
      width: "24px",
      cursor: "pointer",
    }}
    onClick={() => toggleClipboardItem(manual)}
  />
</div>

              </div>
            ))}
        </div>
  {!categoryId && (
    <div className="profileManualReads manualsContainer" style={{ marginTop: "20px" }}>
      
      <div className="profileManualHeader">
        <h3>Unread Manuals</h3>

        <span className="manualCount">
          {unreadUserManuals.length}
        </span>
      </div>

      {unreadUserManuals.length === 0 ? (

        <p className="noManuals">
          You have read all manuals
        </p>

      ) : (

        <div className="readManualList">

          {unreadUserManuals.map((manual) => {
    const uploadDate =
      manual.uploaded_at ||
      manual.updated_at ||
      manual.created_at;

    return (
      <div
        key={manual.id}
        className="readManualRow"
      >
        <span className="manualTitle">
          {manual.title}
        </span>

        
        <NavLink
  to={`/dashboard/category/${manual.category_id}`}
  className="manualRoute"
>
  {manual.category_path_text ||
    manual.category_name ||
    "Unknown Category"}
</NavLink>


        <small className="manualDate">
          {uploadDate
            ? new Date(uploadDate).toLocaleDateString(
                "en-GB",
                {
                  day: "2-digit",
                  month: "short",
                  year: "numeric",
                }
              )
            : "-"}
        </small>
      </div>
    );
  })}



        </div>
      )}
    </div>
  )}
  {isAdmin && !categoryId && (
  <form
    onSubmit={handleUpload}
    className="manualUploadForm"
    style={{
      padding: "16px",
      borderBottom: "1px solid var(--card-border)",
      display: "flex",
      flexDirection: "column",
      gap: "10px",
    }}
  >
    <input
      placeholder="Manual title"
      value={title}
      onChange={(e) => setTitle(e.target.value)}
      className="uploadInput"
    />

    <select
      value={uploadCategoryId}
      onChange={(e) => setUploadCategoryId(e.target.value)}
      className="uploadInput"
    >
      <option value="">Select Category...</option>

      {categoryOptions.map((cat) => (
        <option
          key={cat.id}
          value={cat.id}
        >
          {cat.label}
        </option>
      ))}
    </select>

    <input
      type="file"
      accept="application/pdf"
      onChange={(e) => setFile(e.target.files[0])}
    />

    <button
      className="uploadBtn"
      disabled={uploading}
    >
      {uploading ? "Uploading..." : "Upload Manual"}
    </button>
  </form>
)}
        {isLeafCategory && (
          <div className="manualsContainer">
  <div
    style={{
      width: "100%",
      height: "100vh",
      position: "relative",
    }}
  >
    {loadingPdf && (
      <div
        style={{
          position: "absolute",
          inset: 0,
          background: "var(--card)",
          zIndex: 100,
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          alignItems: "center",
          gap: "18px",
        }}
      >
        <LoaderCircle
          size={42}
          className="manualLoader"
          color="var(--accent)"
        />

        <div
          style={{
            width: "320px",
            maxWidth: "80%",
            height: "8px",
            background: "var(--card-border)",
            borderRadius: "999px",
            overflow: "hidden",
          }}
        >
          <div
            style={{
              width: `${pdfProgress}%`,
              height: "100%",
              background: "var(--accent)",
              transition: "width .25s ease",
            }}
          />
        </div>

        <span
          style={{
            color: "var(--text)",
            fontSize: "14px",
            fontWeight: 500,
          }}
        >
          Loading manual... {pdfProgress}%
        </span>
      </div>
    )}

    {openDoc ? (
      <iframe
        src={openDoc}
        width="100%"
        height="100%"
        style={{
          border: "none",
          borderRadius: "12px",
        }}
        title="PDF preview"
        onLoad={() => {
          setPdfProgress(100);

          setTimeout(() => {
            setLoadingPdf(false);
          }, 200);
        }}
      />
    ) : (
      <div
        style={{
          height: "100%",
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          color: "var(--text)",
          opacity: 0.7,
          fontSize: "16px",
        }}
      >
        Select a manual to preview
      </div>
    )}
  </div>
</div>
        )}
      </PageWrapper>
    );
  };

  export default Manuals;
