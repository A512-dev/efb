// import { NavLink } from "react-router-dom";
// import { useManuals } from "../hooks/useManuals";
// import { useDownloadManual } from "../hooks/useDownloadManual";
// import downloadSvg from '../assets/icons/Import-File--Streamline-Ultimate.svg'
// import folderSvg from '../assets/icons/Office-Folder--Streamline-Ultimate.svg'
// const Clipboard =( ) =>{
//     const { manuals, loading } = useManuals();
//   const { handleDownload } = useDownloadManual();

//   if (loading) return <p>Loading manuals...</p>;
// return(
//     <>
//     <div className="manualsContainerLeft">
//           <div className="div-header">
//             <NavLink className="card-header1" to={'/dashboard/allDocuments'} active onClick={()=>{ document.querySelector('.manualsContainerLeft').style.height=document.querySelector('.manualsContainerLeft').style.height==='auto' ? '0' : 'auto';}}>all documents </NavLink>
//           <NavLink className="card-header2" to={ '/dashboard/clipboard'} onClick={()=>{ document.querySelector('.manualsContainerLeft').style.height=document.querySelector('.manualsContainerLeft').style.height==='auto' ? '0' : 'auto';}}>Clipboard </NavLink>
          
//         </div>
//           {/* <NavLink className={'headersForManuals'} to="/dashboard/manuals/">A300/600</NavLink>
//           <NavLink to="/dashboard/manuals" className={'headersForManuals'}>Iran Air</NavLink>
//           <NavLink className={'headersForManuals'} to="/dashboard/manuals/chat"> Iranair chat</NavLink>
//           <NavLink className={'headersForManuals'} to="/dashboard/manuals/chat"> Training & resources</NavLink>
//           <NavLink className={'headersForManuals'} to="/dashboard/manuals/chat"> Forms</NavLink>
//           <NavLink className={'headersForManuals'} to="/dashboard/manuals/chat"> Safety issue </NavLink> */}
          
//           {/* <NavLink to="/dashboard/safetyIssue" className={'headersForManuals'}><img src={safetyIssueSvg} alt="" className="navIcon" /> Safety Issue</NavLink>
//           <NavLink to="/dashboard/trainingIssue" className={'headersForManuals'}><img src={trainingIssueSvg} alt="" className="navIcon" /> Training Issue</NavLink> */}
//           {/* <NavLink to="/dashboard/checkList" className={'headersForManuals'}><img src={checkListSvg} alt="" className="navIcon" /> Check list</NavLink>   */}
    
          
//           {/* <h5 className="headersForManuals" onClick={()=>{ document.querySelector('.manualsContainerLeft').style.height=document.querySelector('.manualsContainerLeft').style.height==='auto' ? '0' : 'auto';}}><img src={folderSvg} alt="" style={{width:"16px ",marginRight:'6%'}}/>training issue</h5> */}
//           {/* <h5 className="headersForManuals" onClick={()=>{ document.querySelector('.manualsContainerLeft').style.height=document.querySelector('.manualsContainerLeft').style.height==='auto' ? '0' : 'auto';}}><img src={folderSvg} alt="" style={{width:"16px ",marginRight:'6%'}}/>Operational</h5>
//           <h5 className="headersForManuals" onClick={()=>{ document.querySelector('.manualsContainerLeft').style.height=document.querySelector('.manualsContainerLeft').style.height==='auto' ? '0' : 'auto';}}><img src={folderSvg} alt="" style={{width:"16px ",marginRight:'6%'}}/>Flight Manuals</h5>
//           <h5 className="headersForManuals" onClick={()=>{ document.querySelector('.manualsContainerLeft').style.height=document.querySelector('.manualsContainerLeft').style.height==='auto' ? '0' : 'auto';}}> <img src={folderSvg} alt="" style={{width:"16px ",marginRight:'6%'}}/>SOPs </h5>
//           <h5 className="headersForManuals" onClick={()=>{ document.querySelector('.manualsContainerLeft').style.height=document.querySelector('.manualsContainerLeft').style.height==='auto' ? '0' : 'auto';}}><img src={folderSvg} alt="" style={{width:"16px ",marginRight:'6%'}}/>Training </h5>
//           <h5 className="headersForManuals" onClick={()=>{ document.querySelector('.manualsContainerLeft').style.height=document.querySelector('.manualsContainerLeft').style.height==='auto' ? '0' : 'auto';}}> <img src={folderSvg} alt="" style={{width:"16px ",marginRight:'6%'}} />Checklists </h5> */}
//         </div>
//         {/* <div className="manualsContainer">
    
//       <h2 className="card-header">Manuals</h2>
    
    
//       {manuals.map((manual) => (
//         <div key={manual.id} className="manualItem">
    
//           <div className="manualLeft">
            
    
//             <div>
//               <h3>{manual.title}</h3>
//               <p>{manual.original_filename}</p>
//             </div>
//           </div>
    
//           <button
//             onClick={() => handleDownload(manual)}
//             className="downloadBtn"
//           >
//             <img src={downloadSvg} style={{width:"16px"}}/>
//             Download
//           </button>
    
//         </div>
//       ))}
    
//     </div> */}
//     </>
// )
// }
// // export default Clipboard


// import React, { useContext } from 'react';
// import { BookmarkContext } from '../auth/BookmarkContext';
// import { NavLink } from 'react-router-dom';
// import { useState } from 'react';
// import { useManuals } from "../hooks/useManuals";
// import { useDownloadManual } from "../hooks/useDownloadManual";
// import bookmarkIcon from "../assets/icons/bookmarkadd.svg"

// const Clipboard = () => {
//   const { showBookmarkText } = useContext(BookmarkContext);
//     const { manuals, loading } = useManuals();
//   const { handleDownload } = useDownloadManual();
//   const [showSOP, setShowSOP] = useState(false);
//   const { toggleBookmarkText,toggleSOPInClipboard } = useContext(BookmarkContext);
// const handleBookmarkClick = () => {
//     setShowSOP(prev => !prev);
//     toggleBookmarkText();  };
//   if (loading) return <p>Loading manuals...</p>
  
//   return (
//     <>
//       <div className="manualsContainerLeft">
//               <div className="div-header">
//                 <NavLink className="card-header1" to={'/dashboard/allDocuments'}>all documents </NavLink>
//                 <NavLink className="card-header2 active" to={'/dashboard/clipboard'}>
//                   Clipboard
//                 </NavLink>
//               </div>
      
//               <div style={{ display: 'inline-flex' }}>
//                 {showSOP&& (<p className="headersForManuals" onClick={handleBookmarkClick}>
//                   A30e6-310-SOP
//                 </p>)}
                  
                
                
//               </div>
//             </div>

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

// export default Clipboard;

// import React from 'react'; // useContext را لازم نداریم اگر از useBookmark استفاده کنیم
// import { NavLink } from 'react-router-dom';
// import { useBookmark } from '../auth/BookmarkContext'; // Import the custom hook
// import { useManuals } from "../hooks/useManuals";
// import { useDownloadManual } from "../hooks/useDownloadManual";
// import bookmarkIcon from "../assets/icons/bookmarkadd.svg"; // این دیگر لازم نیست
// const [showSOP, setShowSOP] = useState(false); // این state محلی حذف می‌شود
// const { toggleBookmarkText } = useContext(BookmarkContext); // این هم لازم نیست در اینجا
// const handleBookmarkClick = () => { // این تابع هم حذف می‌شود

//   setShowSOP(prev => !prev);
//   toggleBookmarkText();
// };

// const Clipboard = () => {
//   // Get states from the context using the custom hook
//   const { showBookmarkText, showSOPInClipboard } = useBookmark();
//   const { manuals, loading } = useManuals();
//   const { handleDownload } = useDownloadManual();

//   if (loading) return <p>Loading manuals...</p>;

//   return (
//     <>
//       <div className="manualsContainerLeft">
//         <div className="div-header">
//           {/* مطمئن شوید مسیرها درست هستند */}
//           <NavLink className="card-header1" to={'/dashboard/allDocuments'}>all documents </NavLink>
//           <NavLink className="card-header2 active" to={'/dashboard/clipboard'}>
//             Clipboard
//           </NavLink>
//         </div>

//         {/* نمایش SOP فقط زمانی که از context فعال شده باشد */}
//         {/* از showSOPInClipboard به جای showSOP استفاده کنید */}
//         {showSOPInClipboard && (
//           <p className="headersForManuals">
//             A30e6-310-SOP
//           </p>
//         )}
//       </div>

//       <div className="manualsContainer">
//         {/* متن اضافی که قبلا در Clipboard نمایش داده میشد */}
//         {showBookmarkText && <p>این متن از AircraftDocuments اضافه شده است!</p>}

//         <div style={{ width: '100%', height: '100vh' }}>
//           {/* نمایش PDF فقط زمانی که SOP نمایش داده می شود */}
//           {/* از showSOPInClipboard به جای showSOP استفاده کنید */}
//           {showSOPInClipboard && (
//             <object
//               data="/A306-310-SOP.pdf"
//               type="application/pdf"
//               width="100%"
//               height="100%"
//             >
//               {/* Fallback content */}
//               This browser does not support PDFs. Please download the PDF to view it: <a href="/A306-310-SOP.pdf">Download PDF</a>
//             </object>
//           )}
//         </div>
//       </div>
//     </>
//   );
// };

// export default Clipboard;

import React, { useState } from 'react';
import { NavLink } from 'react-router-dom';
import { useBookmark } from '../auth/BookmarkContext'; 
import { useManuals } from "../hooks/useManuals";
import { useDownloadManual } from "../hooks/useDownloadManual";


const Clipboard = () => {
  
  const { showBookmarkText, showSOPInClipboard } = useBookmark();
  const { manuals, loading } = useManuals();
  const { handleDownload } = useDownloadManual();
  const[showDoc,setShowDoc]= useState('');
  if (loading) return <p>Loading manuals...</p>;

  return (
    <>
      <div className="manualsContainerLeft">
        <div className="div-header">
          <NavLink className="card-header1" to={'/dashboard/allDocuments'}>all documents </NavLink>
          <NavLink className="card-header2 active" to={'/dashboard/clipboard'}>
            Clipboard
          </NavLink>
        </div>

        
        {showSOPInClipboard && (
          <p className="headersForManuals" onClick={()=>{ setShowDoc(!showDoc)}}> 
            A30e6-310-SOP
          </p>
        )}
      </div>

      <div className="manualsContainer">
        
        

        <div style={{ width: '100%', height: '100vh' }}>
          
          {showDoc && (
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

export default Clipboard;
