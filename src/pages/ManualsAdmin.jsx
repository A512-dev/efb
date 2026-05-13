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

import { useState } from "react";
import { useManuals } from "../hooks/useManuals";
import { useDownloadManual } from "../hooks/useDownloadManual";
import { useDeleteManual } from "../hooks/useDeleteManual";
import { getManuals, uploadManual } from "../services/apiService";
import downloadSvg from '../assets/icons/Import-File--Streamline-Ultimate.svg'
const ManualsAdmin = () => {

  const [title, setTitle] = useState("");
  const [file, setFile] = useState(null);


  const { manuals, setManuals, loading } = useManuals();
  const { handleDownload } = useDownloadManual();
  const { handleDelete, loading: deleteLoading } = useDeleteManual((manualId) => {
  
    setManuals(prev => prev.filter(m => m.id !== manualId));
  });

  
 

const handleSubmit = async (e) => {
  e.preventDefault();

  if (!title.trim()) {
    alert("Title is required");
    return;
  }

  if (!file) {
    alert("Please select a file");
    return;
  }

  try {
    const newManual = await uploadManual(file, title);

    setManuals((prev) => [...prev, newManual]);

    alert(`Manual "${title}" uploaded successfully`);

    setTitle("");
    setFile(null);
  } catch (err) {
    if (err.response?.status === 500) {
      alert(`Manual with file "${file.name}" already exists`);

      try {
        const manuals = await getManuals();

        const exists = manuals.some(
          (m) => m.original_filename === file.name
        );

        if (exists) {
          setManuals(manuals);
        }
      } catch (fetchErr) {
        console.error("Failed to refresh manuals", fetchErr);
      }
    } else {
      console.error("Upload error:", err);
      alert("Upload failed");
    }
  }
};

  return (
    <div className="manualsAdminContainer">

  

  <form onSubmit={handleSubmit} className="manualUploadForm">
    <input
      type="text"
      placeholder="Manual title"
      value={title}
      onChange={(e) => setTitle(e.target.value)}
      className="uploadInput"
    />

    <input
      type="file"
      accept="application/pdf"
      onChange={(e) => setFile(e.target.files[0])}
      className="uploadInput"
    />

    <button type="submit" className="uploadBtn">
      Upload
    </button>
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
            <p>{manual.original_filename}</p>
          </div>
        </div>

        <div className="manualActions">
          <button
            onClick={() => handleDownload(manual)}
            className="downloadBtn"
          >
            <img src={downloadSvg} alt="" className="downloadIcon" />
            Download
          </button>

          <button
            onClick={() => {
              const confirmed = window.confirm(
                `Are you sure you want to delete this manual?\n\n"${manual.title}"`
              );
              if (!confirmed) return;

              handleDelete(manual.id)
                .then(() => alert(`Manual "${manual.title}" deleted successfully`))
                .catch(() => alert("Delete failed"));
            }}
            disabled={deleteLoading}
            className="deleteBtn"
          >
            {deleteLoading ? "Deleting..." : "Delete"}
          </button>
        </div>
      </div>
    ))
  )}
</div>

  );
};

export default ManualsAdmin;
