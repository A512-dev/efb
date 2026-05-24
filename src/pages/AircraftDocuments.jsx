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

import React from 'react'; // useState حذف می‌شود
import { NavLink } from "react-router-dom";
import { useManuals } from "../hooks/useManuals";
import { useDownloadManual } from "../hooks/useDownloadManual";
import downloadSvg from '../assets/icons/Import-File--Streamline-Ultimate.svg'
import folderSvg from '../assets/icons/Office-Folder--Streamline-Ultimate.svg'
import bookmarkIcon from '../assets/icons/bookmarkadd.svg'
import backIcon from '../assets/icons/arrowback.svg'
// import { BookmarkContext } from "../auth/BookmarkContext"; // این خط لازم نیست اگر از useBookmark استفاده کنیم
// import { useContext } from "react"; // این خط لازم نیست
// import { useState } from "react"; // این خط لازم نیست
import { useBookmark } from '../auth/BookmarkContext'; // Import the custom hook

const AircraftDocuments = () => {
  const { manuals, loading } = useManuals();
  const { handleDownload } = useDownloadManual();
  const { showBookmarkText, showSOPInClipboard } = useBookmark();
  // const [showSOP, setShowSOP] = useState(false); // حذف state محلی
  const { toggleBookmarkText, toggleSOPInClipboard } = useBookmark(); // دریافت توابع از context

  if (loading) return <p>Loading manuals...</p>;

  const handleBookmarkClick = () => {
    // setShowSOP(prev => !prev); // حذف این خط
    toggleBookmarkText(); // برای نمایش متن در Clipboard
    toggleSOPInClipboard(); // برای نمایش SOP در Clipboard
    console.log("Bookmark clicked! Toggling states via context."); // برای دیباگ
  };

  return (
    <>
      <div className="manualsContainerLeft">
        <div className="div-header">
          <NavLink className="card-header1" to={'/dashboard/a300_600'}>
            <img src={backIcon} style={{width:'25px'}} alt="" />
          </NavLink>
          <NavLink className="card-header2 active" to={'/dashboard/clipboard'}>
            Aircraft documents
          </NavLink>
        </div>

        <div style={{ display: 'inline-flex', alignItems: 'center' }}> {/* Align items vertically */}
          {/* این پاراگراف SOP فقط در AircraftDocuments نمایش داده می‌شود تا زمانی که فعال شده باشد */}
          {/* نمایش آن به context وابسته نیست، بلکه فقط متن نشان داده می‌شود */}
          <p className="headersForManuals" onClick={handleBookmarkClick} style={{cursor: 'pointer'}}> {/* Add cursor pointer */}
            A30e6-310-SOP
          </p>
          <img
              src={bookmarkIcon}
              onClick={handleBookmarkClick}
              alt="Bookmark"
              className="imgBookmark active" // اگر کلاس active معنی خاصی دارد نگه دارید
              style={{
                width: '25px',
                marginLeft: '1em',
                marginBottom: '-.3em',
                cursor: 'pointer',
              }}
            />
        </div>
      </div>

      <div className="manualsContainer">
        <div style={{ width: '100%', height: '100vh' }}>
          {showSOPInClipboard && (
            <object
              data="/A306-310-SOP.pdf"
              type="application/pdf"
              width="100%"
              height="100%"
            >
          
              This browser does not support PDFs. Please download the PDF to view it: <a href="/A306-310-SOP.pdf">Download PDF</a>
            </object>
          )}
        </div>
      </div>
    </>
  );
};

export default AircraftDocuments;
