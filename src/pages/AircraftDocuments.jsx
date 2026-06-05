// import { NavLink } from "react-router-dom";
// import { useManuals } from "../hooks/useManuals";
// import { useDownloadManual } from "../hooks/useDownloadManual";
// import downloadSvg from '../assets/icons/Import-File--Streamline-Ultimate.svg'
// import folderSvg from '../assets/icons/Office-Folder--Streamline-Ultimate.svg'
// import bookmarkIcon from '../assets/icons/bookmarkadd.svg'
// import { useState } from "react";
// // import { BookmarkContext } from "../auth/BookmarkContext";
// import { useContext } from "react";
// const AircraftDocuments = ()=>{
//     const { manuals, loading } = useManuals();
//   const { handleDownload } = useDownloadManual();
// const [showSOP,setShowSOP]=useState(false);
// // const { toggleBookmarkText } = useContext(BookmarkContext);

//   if (loading) return <p>Loading manuals...</p>;
  
 
// return (
//     <>
//     <div className="manualsContainerLeft">
//       <div className="div-header">
//         <NavLink className="card-header1" to={'/dashboard/a300_600'}> Back </NavLink>
//       <NavLink className="card-header2 active" to={ '/dashboard/clipboard'} >Aircraft documents </NavLink>
      
//     </div>
      
      
//       <div  style={{display:'inline-flex'}}>
//         <p className="headersForManuals" onClick={()=>{setShowSOP(!showSOP)}}> A30e6-310-SOP <img src={bookmarkIcon} alt="" className="navIcon" style={{width:'25px' ,marginLeft:'2em',marginTop:'.8em',marginBottom:'-.3em'}}/></p>
//       </div>
      
      
      
      
//     </div>
//     <div className="manualsContainer">

  

// <div style={{ width: "100%", height: "100vh"}}>
//   {showSOP && (
//   <object
//     data="/A306-310-SOP.pdf"
//     type="application/pdf"
//     width="100%"
//     height="100%"
//   >
//     <p>مرورگر شما نمی‌تواند فایل PDF را نمایش دهد. 
//        <a href="/A306-310-SOP.pdf">دانلود فایل</a>
//     </p>
//   </object>
// )}

      
//     </div>
  
// </div>
//     </>
// )
// }

// export default AircraftDocuments;

// import { NavLink } from "react-router-dom";
// import { useManuals } from "../hooks/useManuals";
// import { useDownloadManual } from "../hooks/useDownloadManual";
// import downloadSvg from '../assets/icons/Import-File--Streamline-Ultimate.svg'
// import folderSvg from '../assets/icons/Office-Folder--Streamline-Ultimate.svg'
// import bookmarkIcon from '../assets/icons/bookmarkadd.svg'
// import { BookmarkContext } from "../auth/BookmarkContext";
// import { useContext } from "react";
// import { useState } from "react";
// const AircraftDocuments = () => {
//   const { manuals, loading } = useManuals();
//   const { handleDownload } = useDownloadManual();
//   const [showSOP, setShowSOP] = useState(false);
//   const { toggleBookmarkText } = useContext(BookmarkContext);

//   if (loading) return <p>Loading manuals...</p>;

//   const handleBookmarkClick = () => {
//     setShowSOP(prev => !prev);
//     toggleBookmarkText();  };

//   return (
//     <>
//       <div className="manualsContainerLeft">
//         <div className="div-header">
//           <NavLink className="card-header1" to={'/dashboard/a300_600'}>
//             Back
//           </NavLink>
//           <NavLink className="card-header2 active" to={'/dashboard/clipboard'}>
//             Aircraft documents
//           </NavLink>
//         </div>

//         <div style={{ display: 'inline-flex' }}>
//           <p className="headersForManuals" onClick={handleBookmarkClick}>
//             A30e6-310-SOP
//           </p>
//           <img
//               src={bookmarkIcon} onClick={handleBookmarkClick}
//               alt=""
//               className="imgBookmark active"
//               style={{
//                 width: '25px',
//                 marginLeft: '1em',
                
//                 marginBottom: '-.3em',
//                 cursor: 'pointer',
//               }}
//             />
//         </div>
//       </div>

//       <div className="manualsContainer">
//         <div style={{ width: '100%', height: '100vh' }}>
//           {showSOP && (
//             <object
//               data="/A306-310-SOP.pdf"
//               type="application/pdf"
//               width="100%"
//               height="100%"
//             >
              
//             </object>
//           )}
//         </div>
//       </div>
//     </>
//   );
// };

// export default AircraftDocuments;

// import React from 'react';
// import { NavLink } from "react-router-dom";
// import { useManuals } from "../hooks/useManuals";
// import { useDownloadManual } from "../hooks/useDownloadManual";
// import downloadSvg from '../assets/icons/Import-File--Streamline-Ultimate.svg'
// import folderSvg from '../assets/icons/Office-Folder--Streamline-Ultimate.svg'
// import bookmarkIcon from '../assets/icons/bookmarkadd.svg'
// import backIcon from '../assets/icons/arrowback.svg'
// import bookmarkfill from '../assets/icons/bookmarkpor.svg'
// import bookmarkunfill from '../assets/icons/bookmarkadd.svg'
// import { useBookmark } from '../auth/BookmarkContext';

// const AircraftDocuments = () => {
//   const { manuals, loading } = useManuals();
//   const { handleDownload } = useDownloadManual();
//   const { showBookmarkText, showSOPInClipboard } = useBookmark();
//   const { toggleBookmarkText, toggleSOPInClipboard } = useBookmark(); 

//   if (loading) return <p>Loading manuals...</p>;

//   const handleBookmarkClick = () => {
    
//     toggleBookmarkText();
//     toggleSOPInClipboard();
//     console.log("Bookmark clicked! Toggling states via context.");
//   };

//   return (
//     <>
//       <div className="manualsContainerLeft">
//         <div className="div-header">
//           <NavLink className="card-header1" to={'/dashboard/a300_600'}>
//             <img src={backIcon} style={{width:'25px'}} alt="" />
//           </NavLink>
//           <NavLink className="card-header2 active" to={'/dashboard/clipboard'}>
//             Aircraft documents
//           </NavLink>
//         </div>

//         <div style={{ display: 'inline-flex', alignItems: 'center' }}> 
//           <p className="headersForManuals" onClick={handleBookmarkClick} style={{cursor: 'pointer'}}>
//             A30e6-310-SOP
//           </p>
//           <img
//               src={bookmarkfill}
//               onClick={handleBookmarkClick}
//               alt="Bookmark"
//               className="imgBookmark"
//               style={{
//                 width: '25px',
//                 marginLeft: '1em',
//                 marginBottom: '-.3em',
//                 cursor: 'pointer',
//               }}
//             />
//         </div>
//       </div>

//       <div className="manualsContainer">
//         <div style={{ width: '100%', height: '100vh' }}>
//           {showSOPInClipboard && (
//             <object
//               data="/A306-310-SOP.pdf"
//               type="application/pdf"
//               width="100%"
//               height="100%"
//             >
          
//               This browser does not support PDFs. Please download the PDF to view it: <a href="/A306-310-SOP.pdf">Download PDF</a>
//             </object>
//           )}
//         </div>
//       </div>
//     </>
//   );
// };

// export default AircraftDocuments;

import React from 'react';
import { NavLink } from "react-router-dom";
import { useManuals } from "../hooks/useManuals";
import { useDownloadManual } from "../hooks/useDownloadManual";

import backIcon from '../assets/icons/arrowback.svg';

import bookmarkfill from '../assets/icons/bookmarkpor.svg';
import bookmarkunfill from '../assets/icons/bookmarkadd.svg';

import { useBookmark } from '../Context/BookmarkContext';
import PageWrapper from '../components/PageWrapper';

const AircraftDocuments = () => {

  const { manuals, loading } = useManuals();
  const { handleDownload } = useDownloadManual();

  const {
    handleBookmarkIconToggle,
    isDocumentBookmarked,
    showDoc,
    setShowDoc
  } = useBookmark();

  if (loading) return <p>Loading manuals...</p>;

  const handleBookmarkClick = () => {
    handleBookmarkIconToggle({
      title: "A306-310-SOP",
      file: "/A306-310-SOP.pdf"
    });
  };

  const handleOpenPdfClick = () => {
  const file = "/A306-310-SOP.pdf";

  if (showDoc === file) {
    setShowDoc(null);
  } else {
    setShowDoc(file);
  }
};


  const bookmarkImageSrc = isDocumentBookmarked("A306-310-SOP")
    ? bookmarkfill
    : bookmarkunfill;

  return (
    <>
      <PageWrapper>

        <div className="manualsContainerLeft">
          <div className="div-header">

            <NavLink className="card-header1" to={'/dashboard/a300_600'}>
              <img src={backIcon} style={{ width: '25px' }} alt="" />
            </NavLink>

            <NavLink className="card-header2 active" to={'/dashboard/clipboard'}>
              Aircraft documents
            </NavLink>

          </div>

          <p
            className="headersForManuals"
            onClick={handleOpenPdfClick}
            style={{ cursor: 'pointer' }}
          >
            A30e6-310-SOP
          </p>

          <img
            src={bookmarkImageSrc}
            onClick={handleBookmarkClick}
            alt="Bookmark"
            className="imgBookmark"
            style={{
              position: 'absolute',
              right: '8%',
              width: '25px',
              marginLeft: '1em',
              marginTop: '-35px',
              cursor: 'pointer'
            }}
          />

        </div>

        <div className="manualsContainer">
          <div style={{ width: '100%', height: '100vh' }}>

            {showDoc && (
              <object
                data={showDoc}
                type="application/pdf"
                width="100%"
                height="100%"
              >
                This browser does not support PDFs.
                <a href={showDoc}>Download PDF</a>
              </object>
            )}

          </div>
        </div>

      </PageWrapper>
    </>
  );
};

export default AircraftDocuments;
