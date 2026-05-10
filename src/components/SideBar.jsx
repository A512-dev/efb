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
import { useAuth } from "../auth/useAuth";

const SideBar = () =>{
 
  const { user, logout } = useAuth();

  if (!user) return null;

  return (
    <aside className="sidebar">
      <h3>SkytechSharif</h3>

      

      {(user.role === "pilot" || user.role === "admin") && (
        <>
        <NavLink className={'nav-item'} to="/dashboard/profile">Me</NavLink>
        <NavLink className={'nav-item'} to="/dashboard/forms">Forms</NavLink>
        
        </>
      )}

      <NavLink to="/dashboard/manuals" className={'nav-item'}>Documents</NavLink>

      {user.role === "admin" && (
        <>
        <NavLink to="/dashboard/manuals-admin" className={'nav-item'}>Manuals Admin</NavLink>
        <NavLink to="/dashboard/add-profile" className={'nav-item'}>Add new Pilot profile</NavLink>
        </>
      )}

      <button onClick={logout}>Logout</button>
      
    </aside>
  );
}
export default SideBar