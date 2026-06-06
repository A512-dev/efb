// import { useManuals } from "../hooks/useManuals";
// import { useDownloadManual } from "../hooks/useDownloadManual";
// import downloadSvg from '../assets/icons/Import-File--Streamline-Ultimate.svg'
// import folderSvg from '../assets/icons/Office-Folder--Streamline-Ultimate.svg'
// import { NavLink } from "react-router-dom";
// import PageWrapper from "../components/PageWrapper";
// const Manuals = () =>{

//   const { manuals, loading } = useManuals();
//   const { handleDownload } = useDownloadManual();

//   if (loading) return <p>Loading manuals...</p>;

//   return (
//     <>
//     <PageWrapper>
//     <div className="manualsContainerLeft">
//       <div className="div-header">
//         <NavLink className="card-header1 active" to={'/dashboard/allDocuments'}>All documents </NavLink>
//       <NavLink className="card-header2"  to={ '/dashboard/clipboard'}>Clipboard </NavLink>
      
//     </div>
//       <NavLink className={'headersForManuals'} to="/dashboard/a300_600">A300/600</NavLink>



//       <NavLink className={'headersForManuals'} to="/dashboard/manuals/chat"> Training & Resources</NavLink>
//       <NavLink className={'headersForManuals'} to="/dashboard/forms"> Forms</NavLink>
//       <NavLink className={'headersForManuals'} to="/dashboard/manuals/chat"> Safety Issue </NavLink>

      
//       {/* <NavLink to="/dashboard/safetyIssue" className={'headersForManuals'}><img src={safetyIssueSvg} alt="" className="navIcon" /> Safety Issue</NavLink>
//       <NavLink to="/dashboard/trainingIssue" className={'headersForManuals'}><img src={trainingIssueSvg} alt="" className="navIcon" /> Training Issue</NavLink> */}
//       {/* <NavLink to="/dashboard/checkList" className={'headersForManuals'}><img src={checkListSvg} alt="" className="navIcon" /> Check list</NavLink>   */}

      
//       {/* <h5 className="headersForManuals" onClick={()=>{ document.querySelector('.manualsContainerLeft').style.height=document.querySelector('.manualsContainerLeft').style.height==='auto' ? '0' : 'auto';}}><img src={folderSvg} alt="" style={{width:"16px ",marginRight:'6%'}}/>training issue</h5> */}
//       {/* <h5 className="headersForManuals" onClick={()=>{ document.querySelector('.manualsContainerLeft').style.height=document.querySelector('.manualsContainerLeft').style.height==='auto' ? '0' : 'auto';}}><img src={folderSvg} alt="" style={{width:"16px ",marginRight:'6%'}}/>Operational</h5>
//       <h5 className="headersForManuals" onClick={()=>{ document.querySelector('.manualsContainerLeft').style.height=document.querySelector('.manualsContainerLeft').style.height==='auto' ? '0' : 'auto';}}><img src={folderSvg} alt="" style={{width:"16px ",marginRight:'6%'}}/>Flight Manuals</h5>
//       <h5 className="headersForManuals" onClick={()=>{ document.querySelector('.manualsContainerLeft').style.height=document.querySelector('.manualsContainerLeft').style.height==='auto' ? '0' : 'auto';}}> <img src={folderSvg} alt="" style={{width:"16px ",marginRight:'6%'}}/>SOPs </h5>
//       <h5 className="headersForManuals" onClick={()=>{ document.querySelector('.manualsContainerLeft').style.height=document.querySelector('.manualsContainerLeft').style.height==='auto' ? '0' : 'auto';}}><img src={folderSvg} alt="" style={{width:"16px ",marginRight:'6%'}}/>Training </h5>
//       <h5 className="headersForManuals" onClick={()=>{ document.querySelector('.manualsContainerLeft').style.height=document.querySelector('.manualsContainerLeft').style.height==='auto' ? '0' : 'auto';}}> <img src={folderSvg} alt="" style={{width:"16px ",marginRight:'6%'}} />Checklists </h5> */}
//     </div>
//     {/* <div className="manualsContainer">

//   <h2 className="card-header">Manuals</h2>


//   {manuals.map((manual) => (
//     <div key={manual.id} className="manualItem">

//       <div className="manualLeft">
        

//         <div>
//           <h3>{manual.title}</h3>
//           <p>{manual.original_filename}</p>
//         </div>
//       </div>

//       <button
//         onClick={() => handleDownload(manual)}
//         className="downloadBtn"
//       >
//         <img src={downloadSvg} style={{width:"16px"}}/>
//         Download
//       </button>

//     </div>
//   ))}

// </div> */}
// </PageWrapper>
// </>
//   );
// }
// export default Manuals

//TODO ------------

// import { useParams } from "react-router-dom";
// import { useManuals } from "../hooks/useManuals";
// import { useDownloadManual } from "../hooks/useDownloadManual";
// import downloadSvg from "../assets/icons/Import-File--Streamline-Ultimate.svg";
// import { NavLink } from "react-router-dom";
// import PageWrapper from "../components/PageWrapper";
// import { useManualCategories } from "../hooks/useManualCategories";

// const Manuals = () => {
//   const { categoryId } = useParams();

//   const { manuals, loading } = useManuals(categoryId || null);
//   const { handleDownload } = useDownloadManual();
//   const { categories, loading: categoriesLoading } = useManualCategories();

//   if (loading) return <p>Loading manuals...</p>;
//   if (categoriesLoading) return <p>Loading categories...</p>;
// console.log("categoryId:", categoryId);
// console.log("manuals:", manuals);

//   return (
//     <PageWrapper>
//       <div className="manualsContainerLeft">
//         <div className="div-header">
//           <NavLink
//             className="card-header1"
//             to="/dashboard/allDocuments"
//           >
//             All documents
//           </NavLink>

//           <NavLink
//             className="card-header2"
//             to="/dashboard/clipboard"
//           >
//             Clipboard
//           </NavLink>
//         </div>

//         {categories && categories.map((category) => (
//           <NavLink
//             key={category.id}
//             className="headersForManuals"
//             to={`/dashboard/category/${category.id}`}
//           >
//             {category.name}
//           </NavLink>
//         ))}
//       </div>

//       <div className="manualsContainer">
//         <h2 className="card-header">Manuals</h2>

//         {manuals.length === 0 && (
//           <p>No manuals found in this category.</p>
//         )}

//         {manuals.map((manual) => (
//           <div key={manual.id} className="manualItem">
//             <div className="manualLeft">
//               <div>
//                 <h3>{manual.title}</h3>
//                 <p>{manual.original_filename}</p>
//               </div>
//             </div>

//             <button
//               onClick={() => handleDownload(manual)}
//               className="downloadBtn"
//             >
//               <img src={downloadSvg} alt="" style={{ width: "16px" }} />
//               Download
//             </button>
//           </div>
//         ))}
//       </div>
//     </PageWrapper>
//   );
// };

// export default Manuals;

import { useParams, NavLink } from "react-router-dom";
import { useState, useEffect } from "react";
import { useManuals } from "../hooks/useManuals";
import { useDownloadManual } from "../hooks/useDownloadManual";
import { useManualCategories } from "../hooks/useManualCategories";
import { useBookmark } from "../Context/BookmarkContext";
import PageWrapper from "../components/PageWrapper";
import { downloadManual } from "../services/apiService";

import downloadSvg from "../assets/icons/Import-File--Streamline-Ultimate.svg";
import bookmarkAddIcon from "../assets/icons/bookmarkadd.svg";
import bookmarkRemoveIcon from "../assets/icons/bookmarkpor.svg";

const Manuals = () => {
  const { categoryId } = useParams();

  const { categories, loading: categoriesLoading } =
    useManualCategories(categoryId || null);

  const isLeafCategory = !categories || categories.length === 0;

  const { manuals, loading } = useManuals(
    isLeafCategory ? categoryId || null : null
  );

  const { handleDownload } = useDownloadManual();
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
          categories.map((category) => (
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

              <div style={{ display: "flex", gap: "2px",position:'absolute',right:'20px' }}>
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

                <img
                  src={downloadSvg}
                  alt="download"
                  style={{ width: "24px", cursor: "pointer" }}
                  onClick={() => handleDownload(manual)}
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
