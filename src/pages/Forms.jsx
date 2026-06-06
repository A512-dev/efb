// import React from 'react';
// import { NavLink } from "react-router-dom";
// import { useManuals } from "../hooks/useManuals";
// import { useDownloadManual } from "../hooks/useDownloadManual";
// import backIcon from '../assets/icons/arrowback.svg'
// import { useBookmark } from '../auth/BookmarkContext';

// const Forms = () =>{
// const { manuals, loading } = useManuals();
//   const { handleDownload } = useDownloadManual();
//   const { showBookmarkText, showSOPInClipboard } = useBookmark();
//   const { toggleBookmarkText, toggleSOPInClipboard } = useBookmark(); 
//   if (loading) return <p>Loading manuals...</p>;
//   const handleBookmarkClick = () => {
    
//     toggleBookmarkText();
//     toggleSOPInClipboard();
//     console.log("Bookmark clicked! Toggling states via context.");
//   };
//     return (
//         <>
//         <div className="manualsContainerLeft">
//         <div className="div-header">
//           <NavLink className="card-header1" to={'/dashboard/a300_600'}>
//             <img src={backIcon} style={{width:'25px'}} alt="" />
//           </NavLink>
//           <NavLink className="card-header2 active">
//             Forms
//           </NavLink>
//         </div>

//         <div style={{ display: 'inline-flex', alignItems: 'center' }}> 
//           <p className="headersForManuals" onClick={handleBookmarkClick} style={{cursor: 'pointer'}}> 
//             ASR
//           </p>
          
//         </div>
//       </div>
//         {/* <div style={{ height: "90vh" }}>
//         <PDFViewer
//         document={{
//           url: "../assets/files/Air Safety Report.pdf",
//         }}
//       />
//     </div> */}
//     <div style={{ width: "60%", height: "100vh" ,position:"absolute" ,right:'20px',top:'60px'}}>
//       {}
//       <object
//               data="/Air Safety Report.pdf"
//               type="application/pdf"
//               width="100%"
//               height="100%"
//             >
          
//               This browser does not support PDFs. Please download the PDF to view it: <a href="/A306-310-SOP.pdf">Download PDF</a>
//             </object>
//     </div>
//         </>
//     )
// }
// export default Forms
// import React from 'react';
// import { NavLink } from "react-router-dom";
// import { useManuals } from "../hooks/useManuals";
// import { useDownloadManual } from "../hooks/useDownloadManual";
// import backIcon from '../assets/icons/arrowback.svg';
// import { useBookmark } from '../auth/BookmarkContext'; // Import the custom hook

// const Forms = () => {
//   const { manuals, loading } = useManuals();
//   const { handleDownload } = useDownloadManual();

//   // دریافت state های مربوط به SOP و ASR و همچنین تابع manageASR
//   const {
//     showBookmarkText,
//     showSOPInClipboard,
//     showASRInClipboard, // state جدید ASR
//     manageASR, // تابع مدیریت کلیک برای ASR و بوکمارک
//     toggleSOP // تابع برای toggle کردن SOP
//   } = useBookmark();

//   if (loading) return <p>Loading manuals...</p>;

//   // تابعی که وقتی روی متن "ASR" کلیک می‌شود، فراخوانی می‌شود.
//   // این تابع manageASR را صدا می‌زند که وضعیت ASR و آیکون بوکمارک را تغییر می‌دهد.
//   const handleASRClick = () => {
//     manageASR();
//     console.log("ASR clicked! Toggling ASR and bookmark icon.");
//   };

//   // تابعی که وقتی روی متن "SOP" کلیک می‌شود (اگر دکمه یا متنی برای آن دارید)
//   const handleSOPClick = () => {
//     toggleSOP();
//     console.log("SOP clicked! Toggling SOP state.");
//   };

//   return (
//     <>
//       <div className="manualsContainerLeft">
//         <div className="div-header">
//           <NavLink className="card-header1" to={'/dashboard/a300_600'}>
//             <img src={backIcon} style={{ width: '25px' }} alt="" />
//           </NavLink>
//           <NavLink className="card-header2 active">
//             Forms
//           </NavLink>
//         </div>

//         {/* نمایش پاراگراف ASR به صورت شرطی */}
//         {/* وقتی showASRInClipboard فعال باشد، متن ASR نمایش داده می‌شود */}
//         <div style={{ display: 'inline-flex', alignItems: 'center' }}>
//           <p className="headersForManuals" onClick={handleASRClick} style={{ cursor: 'pointer' }}>
//             ASR
//           </p>
//           {/* اینجا آیکون بوکمارک را اضافه می‌کنیم.
//               اگر بخواهید آیکون بوکمارک فقط با کلیک روی ASR تغییر کند،
//               باید وضعیت آن را از context دریافت کنید و استایل دهید.
//               در حال حاضر، manageASR خودش آیکون را تغییر می‌دهد.
//           */}
//           {/* <img src={currentBookmarkIcon} onClick={handleBookmarkIconClick} ... /> */}
//         </div>

//         {/* نمایش پاراگراف SOP به صورت شرطی (اگر دکمه یا متنی برای آن دارید) */}
//         {/* این بخش را اگر می‌خواهید SOP هم داشته باشید اضافه کنید */}
//         {/*
//         <div style={{ display: 'inline-flex', alignItems: 'center' }}>
//            <p className="headersForManuals" onClick={handleSOPClick} style={{ cursor: 'pointer' }}>
//               SOP
//            </p>
//            // اگر آیکون جداگانه برای SOP دارید، اینجا اضافه کنید
//         </div>
//         */}
//       </div>

//       {/* بخش نمایش PDF ها */}
//       <div style={{ width: "60%", height: "100vh", position: "absolute", right: '20px', top: '60px' }}>
//         {/* نمایش PDF برای ASR اگر showASRInClipboard فعال باشد */}
//         {showASRInClipboard && (
//           <object
//             data="/Air Safety Report.pdf" // مسیر فایل PDF مربوط به ASR
//             type="application/pdf"
//             width="100%"
//             height="100%"
//           >
//             This browser does not support PDFs. Please download the PDF to view it: <a href="/Air Safety Report.pdf">Download PDF</a>
//           </object>
//         )}

//         {/* نمایش PDF برای SOP اگر showSOPInClipboard فعال باشد */}
//         {/* این بخش را اگر می‌خواهید SOP هم در اینجا نمایش داده شود، فعال کنید */}
//         {/*
//         {showSOPInClipboard && (
//           <object
//             data="/A306-310-SOP.pdf" // مسیر فایل PDF مربوط به SOP
//             type="application/pdf"
//             width="100%"
//             height="100%"
//           >
//             This browser does not support PDFs. Please download the PDF to view it: <a href="/A306-310-SOP.pdf">Download PDF</a>
//           </object>
//         )}
//         */}
//       </div>
//     </>
//   )
// }

// export default Forms;

import React from 'react';
import { NavLink } from "react-router-dom";
import { useManuals } from "../hooks/useManuals";
import { useDownloadManual } from "../hooks/useDownloadManual";
import backIcon from '../assets/icons/arrowback.svg';
import { useBookmark } from '../Context/BookmarkContext';
import PageWrapper from '../components/PageWrapper';

const Forms = () => {
  const { manuals, loading } = useManuals();
  const { handleDownload } = useDownloadManual();

  const { showDoc, setShowDoc } = useBookmark();


  if (loading) return <p>Loading manuals...</p>;


const handleASRClick = () => {
  setShowDoc((prev) => (prev === "ASR" ? null : "ASR"));
};


const handleSubmitForm = () => {

  console.log("Submitting ASR form to backend...");
};

  return (
    <>
    <PageWrapper>
      <div className="manualsContainerLeft">
        <div className="div-header">
          <NavLink className="card-header1" to={'/dashboard/allDocuments'}>
            <img src={backIcon} style={{ width: '25px' }} alt="" />
          </NavLink>
          <NavLink className="card-header2 active">
            Forms
          </NavLink>
        </div>

        <div style={{ display: 'inline-flex', alignItems:'center' ,width:'100%', gap: '10px' }}>
  <p
    className="headersForManuals forms"
    onClick={handleASRClick}
    style={{ cursor: 'pointer'}}
  >
    ASR
  </p>

  <button
    className="submit-form-button"
    onClick={handleSubmitForm}
  >
    Submit
  </button>
</div>

      </div>

      <div style={{ width: "60%", height: "100vh", position: "absolute", right: '20px', top: '20px' }}>
        {showDoc === "ASR" && (

          <object
            data="/Air Safety Report.pdf"
            type="application/pdf"
            width="100%"
            height="100%"
          >
            This browser does not support PDFs. Please download the PDF to view it: <a href="/Air Safety Report.pdf">Download PDF</a>
          </object>
        )}

        
      </div>
      </PageWrapper>
    </>
  )
}

export default Forms;
