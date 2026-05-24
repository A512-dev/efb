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

import { NavLink } from "react-router-dom";
import { useState , useEffect } from "react";

import { useAuth } from "../auth/useAuth";
import ThemeToggle from "./themetoggle";
import darkSkyTechPng from '../assets/icons/skytech-logo-transparent-white.webp'
// import lightSkyTechPng from '../assets/icons/Skytech-logo-transparent (1).png'
import documentSvg from '../assets/icons/Common-File-Stack--Streamline-Ultimate copy.svg'
import crewProfileSvg from '../assets/icons/Following-1--Streamline-Ultimate.svg'
import formsSvg from '../assets/icons/Kindle-Hold--Streamline-Ultimate.svg'
import manualsAdminSvg from '../assets/icons/Monitor-Transfer-1--Streamline-Ultimate.svg'
import addPilotSvg from '../assets/icons/Add-Circle-Bold--Streamline-Ultimate.svg'

import safetyIssueSvg from '../assets/icons/Laptop-Warning--Streamline-Ultimate.svg'
import trainingIssueSvg from '../assets/icons/Electronics-Fuse--Streamline-Ultimate.svg'
import checkListSvg from '../assets/icons/Notes-Checklist-Flip--Streamline-Ultimate.svg'
import iranAirLogo from '../assets/icons/iranair-logo (1).png'
const SideBar = () =>{
 
   const [theme, setTheme] = useState("light");

    useEffect(() => {
      setTheme(document.documentElement.getAttribute("data-theme") || "light");
    }, []);
    const { user} = useAuth();

  if (!user) return null;

  return (
    

<aside className="SideBar">
  <img src={iranAirLogo} style={{width:'50%', marginLeft:'25%',marginBottom:'-15%'}} alt="" />
  <h3> IranAir EFB</h3>

  {(user.role === "pilot" || user.role === "admin") && (
    <>
      <NavLink className={'nav-item'} to="/dashboard/profile"><img src={crewProfileSvg} alt="" className="navIcon" /> profile</NavLink>
      <NavLink to="/dashboard/manuals" className={'nav-item'}><img src={documentSvg} alt="" className="navIcon" /> Documents</NavLink>
      <NavLink className={'nav-item'} to="/dashboard/forms"><img src={formsSvg} alt="" className="navIcon" /> Iranair chat</NavLink>
      {/* <NavLink to="/dashboard/safetyIssue" className={'nav-item'}><img src={safetyIssueSvg} alt="" className="navIcon" /> Safety Issue</NavLink>
      <NavLink to="/dashboard/trainingIssue" className={'nav-item'}><img src={trainingIssueSvg} alt="" className="navIcon" /> Training Issue</NavLink> */}
      {/* <NavLink to="/dashboard/checkList" className={'nav-item'}><img src={checkListSvg} alt="" className="navIcon" /> Check list</NavLink>   */}
    </>
  )}

  {user.role === "admin" && (
    <>
      <NavLink to="/dashboard/manuals-admin" className={'nav-item'}><img src={manualsAdminSvg} alt="" className="navIcon" /> Manage</NavLink>
      <NavLink to="/dashboard/add-profile" className={'nav-item'}><img src={addPilotSvg} alt="" className="navIcon" /> Add Pilot</NavLink>
    </>
  )}

  
  <ThemeToggle />
</aside>

  );
}
export default SideBar