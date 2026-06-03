// import { useState } from "react";
// import { NavLink } from "react-router-dom";

// const SideBar=()=>{
//     const [open,setOpen]= useState(false)
// return (
//     <>
//     <div>
//         <button className="menu-btn" onClick={() => setOpen(!open)}>
//         ☰
//       </button>

//       <aside className={`sidebar ${open ? "open" : ""}`}>
//         <h3 className="sidebar-title">Dashboard</h3>

//         <nav className="sidebar-nav">
//           <NavLink to="dashboard" className="nav-item">Home</NavLink>
//           <NavLink to="users" className="nav-item">Users</NavLink>
//           <NavLink to="settings" className="nav-item">Settings</NavLink>
//         </nav>
//       </aside>
//     </div>
//     </>
// )
// }

// export default SideBar

// import { NavLink } from "react-router-dom";
// import { useAuth } from "../auth/useAuth";


// const Sidebar = ()=> {
//   const { user } = useAuth();

//   if (!user) return null;

//   return (
//     <aside className="sidebar">
//       <h3>Dashboard</h3>
//       <nav>
//         {user.role === "pilot" && (
//           <>
//             <NavLink className={'nav-item'} to="forms">Forms</NavLink>
//             <NavLink to="manuals">Manuals</NavLink>
//           </>
//         )}
//         {user.role === "admin" && (
//           <NavLink to="manuals-admin">Update Manuals</NavLink>
//         )}
//       </nav>
//     </aside>
//   );
// }
// export default Sidebar;

// import { NavLink } from "react-router-dom";
// import { useAuth } from "../auth/useAuth";

// export default function Sidebar() {
//   const { user } = useAuth();

//   console.log("Sidebar user:", user); // برای تست

//   if (!user) {
//     return (
//       <aside style={{ width: 200, background: "#eee", padding: 16 }}>
//         <p>کاربر لاگین نشده</p>
//       </aside>
//     );
//   }

//   return (
//     <aside className="sidebar">
//       <h3>Dashboard</h3>
//       <nav style={{ display: "flex", flexDirection: "column", gap: 8 }}>
//         {user.role === "pilot" && (
//           <>
//             <NavLink to="forms">Forms</NavLink>
//             <NavLink to="manuals">Manuals</NavLink>
//           </>
//         )}

//         {user.role === "admin" && (
//           <NavLink to="manuals-admin" className={'nav-item'}>Update Manuals</NavLink>
//         )}
//       </nav>
//     </aside>
//   );
// }

// import { NavLink } from "react-router-dom";
// import { useState , useEffect } from "react";

// import { useAuth } from "../auth/useAuth";
// import ThemeToggle from "./ThemeToggle";
// import darkSkyTechPng from '../assets/icons/skytech-logo-transparent-white.webp'
// import riskicon from "../assets/icons/risk-icon.svg";

// import documentSvg from '../assets/icons/Common-File-Stack--Streamline-Ultimate copy.svg'
// import crewProfileSvg from '../assets/icons/Following-1--Streamline-Ultimate.svg'
// import formsSvg from '../assets/icons/Kindle-Hold--Streamline-Ultimate.svg'
// import manualsAdminSvg from '../assets/icons/Monitor-Transfer-1--Streamline-Ultimate.svg'
// import addPilotSvg from '../assets/icons/Add-Circle-Bold--Streamline-Ultimate.svg'

// import safetyIssueSvg from '../assets/icons/Laptop-Warning--Streamline-Ultimate.svg'
// import trainingIssueSvg from '../assets/icons/Electronics-Fuse--Streamline-Ultimate.svg'
// import checkListSvg from '../assets/icons/Notes-Checklist-Flip--Streamline-Ultimate.svg'
// import iranAirLogo from '../assets/icons/iranair-logo (1).png'
// import chatboxicon from '../assets/icons/download.svg'
// import settingIcon from '../assets/icons/settings.svg'
// const SideBar = () =>{
 
//    const [theme, setTheme] = useState("light");

//     useEffect(() => {
//       setTheme(document.documentElement.getAttribute("data-theme") || "light");
//     }, []);
//     const { user} = useAuth();

//   if (!user) return null;

//   return (
    

// <aside className="SideBar">
//   <img src={iranAirLogo} style={{width:'50%', marginLeft:'25%',marginBottom:'-15%'}} alt="" />
//   <h3> IranAir EFB</h3>

//   {(user.role === "pilot" || user.role === "admin") && (
//     <>
//       <NavLink className={'nav-item'} to="/dashboard/profile"><img src={crewProfileSvg} alt="" className="navIcon" /> Profile</NavLink>
//       <NavLink to="/dashboard/manuals" className={'nav-item'}><img src={documentSvg} alt="" className="navIcon" /> Documents</NavLink>
//       <NavLink className={'nav-item'} to="/dashboard/IranAirChat"><img src={chatboxicon} alt="" className="navIcon chatboxicon" /> IranAir Chat</NavLink>
//       <NavLink className={'nav-item'} to="/dashboard/setting"><img src={settingIcon} alt="" className="navIcon chatboxicon" /> Settings</NavLink>
//       {/* <NavLink to="/dashboard/safetyIssue" className={'nav-item'}><img src={safetyIssueSvg} alt="" className="navIcon" /> Safety Issue</NavLink>
//       <NavLink to="/dashboard/trainingIssue" className={'nav-item'}><img src={trainingIssueSvg} alt="" className="navIcon" /> Training Issue</NavLink> */}
//       {/* <NavLink to="/dashboard/checkList" className={'nav-item'}><img src={checkListSvg} alt="" className="navIcon" /> Check list</NavLink>   */}
//     </>
//   )}

//   {user.role === "admin" && (
//     <>
//       <NavLink to="/dashboard/manuals-admin" className={'nav-item'}><img src={manualsAdminSvg} alt="" className="navIcon" /> Manage</NavLink>
//       <NavLink to="/dashboard/add-profile" className={'nav-item'}><img src={addPilotSvg} alt="" className="navIcon" /> Add Pilot</NavLink>
//     </>
//   )}

  

// </aside>

//   );
// }
// export default SideBar
// import { NavLink } from "react-router-dom";
// import { useState, useEffect, useMemo } from "react";
// import { useAuth } from "../auth/useAuth";

// import documentSvg from "../assets/icons/Common-File-Stack--Streamline-Ultimate copy.svg";
// import crewProfileSvg from "../assets/icons/Following-1--Streamline-Ultimate.svg";
// import manualsAdminSvg from "../assets/icons/Monitor-Transfer-1--Streamline-Ultimate.svg";
// import addPilotSvg from "../assets/icons/Add-Circle-Bold--Streamline-Ultimate.svg";
// import iranAirLogo from "../assets/icons/iranair-logo (1).png";
// import chatboxicon from "../assets/icons/download.svg";
// import settingIcon from "../assets/icons/settings.svg";
// import riskicon from "../assets/icons/risk-icon.svg";
// import skyTechLogo from '../assets/icons/skytech-logo-transparent-white.webp'
// import { getManualUpdates } from "../services/apiService";

// import { listMessages } from "../services/apiService";

// const SideBar = () => {
//   const { user } = useAuth();
//   const [unreadCount, setUnreadCount] = useState(0);
// const [updateCount, setUpdateCount] = useState(0);
// const [isFull, setIsFull] = useState(false);
//   if (!user) return null;

//   const canSeeChat = user.role === "pilot" || user.role === "admin";

//   const fetchUnreadCount = async () => {
//     try {
      
//       const data = await listMessages({ box: "inbox", page: 1, limit: 50 });

//       const items =
//         data?.items || data?.results || data?.data || data?.messages || [];

//       const count = items.filter((m) => !(m.is_read || m.read_at)).length;
//       setUnreadCount(count);
//     } catch (e) {
      
//       console.error(e);
//     }
//   };

//   useEffect(() => {
//     if (!canSeeChat) return;

//     fetchUnreadCount(); 

    
//     const t = setInterval(fetchUnreadCount, 2000);
//     return () => clearInterval(t);
//   }, [canSeeChat]);
// useEffect(() => {
//     let intervalId;

//     const checkManualUpdates = async () => {
//       try {
//         const data = await getManualUpdates();
//         const items = data?.items || data?.results || data?.data || [];

//         if (!items.length) {
//           setIsFull(false);
//           setUpdateCount(0);
//           return;
//         }

//         setIsFull(true);

//         const lastSeenId = localStorage.getItem("manualUpdatesLastSeenId");

//         if (!lastSeenId) {
//           setUpdateCount(items.length);
//           return;
//         }

//         const unseenItems = items.filter(
//           (item) => Number(item.id) > Number(lastSeenId)
//         );

//         setUpdateCount(unseenItems.length);
//       } catch (error) {
//         console.error("Failed to fetch manual updates:", error);
//       }
//     };

//     checkManualUpdates();
//     intervalId = setInterval(checkManualUpdates, 2000);

//     return () => clearInterval(intervalId);
//   }, []);

  
//   useEffect(() => {
//     const handleSeen = () => {
//       setUpdateCount((prev) => (prev > 0 ? prev - 1 : 0));
//     };

//     window.addEventListener("manualUpdateSeen", handleSeen);

//     return () => {
//       window.removeEventListener("manualUpdateSeen", handleSeen);
//     };
//   }, []);

//   const handleUpdatesClick = () => {
//     setUpdateCount((prev) => (prev > 0 ? prev - 1 : 0));
//   };

//   return (
//     <aside className="SideBar">
//       <img
//         src={skyTechLogo}
//         style={{ width: "50%", marginLeft: "25%", marginBottom: "-15%" }}
//         alt=""
//       />
//       <h3> SkyTechSharif</h3>

//       {canSeeChat && (
//         <>
//           <NavLink className="nav-item" to="/dashboard/profile">
//             <img src={crewProfileSvg} alt="" className="navIcon" /> Profile
//           </NavLink>

//           <NavLink to="/dashboard/manuals" className="nav-item">
//             <img src={documentSvg} alt="" className="navIcon" /> Documents
//           </NavLink>

//           <NavLink className="nav-item" to="/dashboard/Chat">
//             <img src={chatboxicon} alt="" className="navIcon chatboxicon" />
//             <span className="nav-text"> Chat</span>

            
//             {unreadCount > 0 && (
//               <span className="chat-unread-badge" title={`${unreadCount} unread`}>
//                 <img src={riskicon} className="imgdangersidebar" alt="unread" />
//                 <span className="chat-unread-count">{unreadCount}</span>
//               </span>
//             )}
//           </NavLink>

//           <NavLink className="nav-item" to="/dashboard/setting">
//             <img src={settingIcon} alt="" className="navIcon chatboxicon" />{" "}
//             Settings
//             {updateCount > 0 && (
//             <span className="update-alert-count">
//               {updateCount}
//             </span>
//           )}
//           </NavLink>
//         </>
//       )}

//       {user.role === "admin" && (
//         <>
//           <NavLink to="/dashboard/manuals-admin" className="nav-item">
//             <img src={manualsAdminSvg} alt="" className="navIcon" /> Manage
//           </NavLink>
//           <NavLink to="/dashboard/add-profile" className="nav-item">
//             <img src={addPilotSvg} alt="" className="navIcon" /> Add Pilot
//           </NavLink>
//         </>
//       )}
//     </aside>
//   );
// };

// export default SideBar;

import { NavLink } from "react-router-dom";
import { useState, useEffect } from "react";
import { useAuth } from "../auth/useAuth";
import { useNotifications } from "../Context/NotificationContext";

import documentSvg from "../assets/icons/Common-File-Stack--Streamline-Ultimate copy.svg";
import crewProfileSvg from "../assets/icons/Following-1--Streamline-Ultimate.svg";
import manualsAdminSvg from "../assets/icons/Monitor-Transfer-1--Streamline-Ultimate.svg";
import addPilotSvg from "../assets/icons/Add-Circle-Bold--Streamline-Ultimate.svg";
import chatboxicon from "../assets/icons/download.svg";
import settingIcon from "../assets/icons/settings.svg";
import riskicon from "../assets/icons/risk-icon.svg";
import iranAirLogo from '../assets/icons/iranair-logo (1).png'

import { listMessages } from "../services/apiService";

const SideBar = () => {
  const { user } = useAuth();
  const { updateCount } = useNotifications();

  const [unreadCount, setUnreadCount] = useState(0);

  if (!user) return null;

  const canSeeChat = user.role === "pilot" || user.role === "admin";

  const fetchUnreadCount = async () => {
    try {
      const data = await listMessages({ box: "inbox", page: 1, limit: 50 });

      const items =
        data?.items || data?.results || data?.data || data?.messages || [];

      const count = items.filter((m) => !(m.is_read || m.read_at)).length;
      setUnreadCount(count);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    if (!canSeeChat) return;

    fetchUnreadCount();
    const t = setInterval(fetchUnreadCount, 5000);

    return () => clearInterval(t);
  }, [canSeeChat]);

  return (
    <aside className="SideBar">
      <img
        src={iranAirLogo}
        style={{ width: "50%", marginLeft: "25%", marginBottom: "-15%" }}
        alt=""
      />

      <h3>IranAir EFB</h3>

      {canSeeChat && (
        <>
          <NavLink className="nav-item" to="/dashboard/profile">
            <img src={crewProfileSvg} alt="" className="navIcon" /> Profile
          </NavLink>

          <NavLink to="/dashboard/manuals" className="nav-item">
            <img src={documentSvg} alt="" className="navIcon" /> Documents
          </NavLink>

          <NavLink className="nav-item" to="/dashboard/Chat">
            <img src={chatboxicon} alt="" className="navIcon chatboxicon" />
            <span className="nav-text">Chat</span>

            {unreadCount > 0 && (
              <span className="chat-unread-badge">
                <img src={riskicon} className="imgdangersidebar" alt="unread" />
                <span className="chat-unread-count">{unreadCount}</span>
              </span>
            )}
          </NavLink>

          <NavLink className="nav-item" to="/dashboard/setting">
            <img src={settingIcon} alt="" className="navIcon chatboxicon" />
            Settings

            {updateCount > 0 && (
              <span className="update-alert-count">{updateCount}</span>
            )}
          </NavLink>
        </>
      )}

      {user.role === "admin" && (
        <>
          <NavLink to="/dashboard/manuals-admin" className="nav-item">
            <img src={manualsAdminSvg} alt="" className="navIcon" /> Manage
          </NavLink>

          <NavLink to="/dashboard/add-profile" className="nav-item">
            <img src={addPilotSvg} alt="" className="navIcon" /> Add Pilot
          </NavLink>
        </>
      )}
    </aside>
  );
};

export default SideBar;
