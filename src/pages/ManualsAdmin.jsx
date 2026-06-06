// import { useState } from "react";
// import { uploadManual } from "../services/apiService";

// const ManualsAdmin = () =>{

//   const [title, setTitle] = useState("");
//   const [file, setFile] = useState(null);

//   const handleSubmit = async (e) => {
//     e.preventDefault();

//     try {
//       await uploadManual(file, title);
//       alert("Manual uploaded successfully");
//     } catch (err) {
//       console.log(err.response?.data);
//     }
//   };

//   return (
//     <form onSubmit={handleSubmit}>

//       <input
//         type="text"
//         placeholder="Manual title"
//         value={title}
//         onChange={(e) => setTitle(e.target.value)}
//       />

//       <input
//         type="file"
//         accept="application/pdf"
//         onChange={(e) => setFile(e.target.files[0])}
//       />

//       <button type="submit">
//         Upload
//       </button>

//     </form>
//   );
// }
// export default ManualsAdmin

import { useState, useEffect } from "react";
import { useManuals } from "../hooks/useManuals";
import { useDownloadManual } from "../hooks/useDownloadManual";
import { useDeleteManual } from "../hooks/useDeleteManual";
import { getManuals, uploadManual, getManualCategories, updateManualPdf } from "../services/apiService";
import downloadSvg from '../assets/icons/Import-File--Streamline-Ultimate.svg';
import PageWrapper from "../components/PageWrapper";

const ManualsAdmin = () => {
  const [title, setTitle] = useState("");
  const [file, setFile] = useState(null);
  const [categoryId, setCategoryId] = useState(""); // استیت برای ذخیره دسته انتخاب شده
  const [categories, setCategories] = useState([]); // لیست دسته‌ها از دیتابیس
  const [updatingId, setUpdatingId] = useState(null);

  const { manuals, setManuals, loading } = useManuals();
  const { handleDownload } = useDownloadManual();
  const { handleDelete, loading: deleteLoading } = useDeleteManual((manualId) => {
    setManuals(prev => prev.filter(m => m.id !== manualId));
  });

  // لود کردن دسته‌بندی‌ها در بدو ورود
  useEffect(() => {
    getManualCategories()
      .then(data => setCategories(data))
      .catch(err => console.error("Failed to load categories", err));
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!title.trim()) { alert("Title is required"); return; }
    if (!file) { alert("Please select a file"); return; }
    if (!categoryId) { alert("Please select a category"); return; }

    const note = window.prompt("Note for this upload (optional):", "") ?? "";

    try {
      // ارسال categoryId به متد آپلود
      const newManual = await uploadManual(file, title, note, categoryId);

      setManuals((prev) => [...prev, newManual]);
      alert(`Manual "${title}" uploaded successfully`);

      setTitle("");
      setFile(null);
      setCategoryId(""); // ریست کردن فرم
    } catch (err) {
      if (err.response?.status === 500) {
        alert(`Manual with file "${file.name}" already exists`);
        const data = await getManuals();
        setManuals(data);
      } else {
        console.error("Upload error:", err);
        alert("Upload failed");
      }
    }
  };

  return (
    <PageWrapper>
      <div className="manualsAdminContainer">
        <form onSubmit={handleSubmit} className="manualUploadForm">
          <input
            type="text"
            placeholder="Manual title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="uploadInput"
          />

          
          <select 
            value={categoryId} 
            onChange={(e) => setCategoryId(e.target.value)}
            className="uploadInput"
            style={{ padding: '8px' }}
          >
            <option value="">Select Category...</option>
            {categories.map(cat => (
              <option key={cat.id} value={cat.id}>{cat.name}</option>
            ))}
          </select>

          <input
            type="file"
            accept="application/pdf"
            onChange={(e) => setFile(e.target.files[0])}
            className="uploadInput"
          />

          <button type="submit" className="uploadBtn">Upload</button>
        </form>

        <h3 className="sectionTitle">All Documents</h3>

        {loading ? (
          <p className="loadingText">Loading manuals...</p>
        ) : (
          manuals.map((manual) => (
            <div key={manual.id} className="manualItem">
              <div className="manualLeft">
                <div>
                  <h4>{manual.title}</h4>
                  <p style={{ fontSize: '12px', color: '#666' }}>
                    {manual.original_filename} | <b>Category: {manual.category_name || 'Uncategorized'}</b>
                  </p>
                </div>
              </div>

              <div className="manualActions">
                <button
                  type="button"
                  className="uploadBtn"
                  disabled={updatingId === manual.id}
                  onClick={() => document.getElementById(`replace-${manual.id}`)?.click()}
                >
                  {updatingId === manual.id ? "Replacing..." : "Replace PDF"}
                </button>

                <input
                  id={`replace-${manual.id}`}
                  type="file"
                  accept="application/pdf"
                  style={{ display: "none" }}
                  onChange={async (e) => {
                    const newFile = e.target.files?.[0];
                    if (!newFile) return;
                    const confirmed = window.confirm(`Replace PDF for "${manual.title}"?`);
                    if (!confirmed) return;

                    try {
                      setUpdatingId(manual.id);
                      const updated = await updateManualPdf(manual.id, newFile, { title: manual.title });
                      setManuals((prev) => prev.map((m) => (m.id === manual.id ? { ...m, ...updated } : m)));
                      alert("Updated successfully");
                    } catch (err) {
                      alert("Update failed");
                    } finally {
                      setUpdatingId(null);
                    }
                  }}
                />

                <button onClick={() => handleDownload(manual)} className="downloadBtn">
                  <img src={downloadSvg} alt="" className="downloadIcon" />
                  Download
                </button>

                <button
                  onClick={async () => {
                    if (window.confirm(`Delete "${manual.title}"?`)) {
                      const note = window.prompt("Reason:", "") ?? "";
                      try {
                        await handleDelete(manual.id, note);
                        alert("Deleted");
                      } catch { alert("Delete failed"); }
                    }
                  }}
                  disabled={deleteLoading}
                  className="deleteBtn"
                >
                  Delete
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </PageWrapper>
  );
};

export default ManualsAdmin;
