import { NavLink } from "react-router-dom";
import ThemeToggle from "../components/ThemeToggle.jsx";
import { useNotifications } from "../Context/NotificationContext";
import { useAuth } from "../auth/useAuth.js";
import logoutSvg from '../assets/icons/Power-Button--Streamline-Ultimate.svg'
import PageWrapper from "../components/PageWrapper.jsx";
import { div } from "framer-motion/client";
import { useState } from "react";
const Setting = () => {
  const { updateCount } = useNotifications();
const { logout } = useAuth();
const [isHelpClicked,setIsHelpClicked]= useState(false)
const [isAboutOpen, setIsAboutOpen] = useState(false);

  return (
    <>
    <PageWrapper>
      <div className="manualsContainerLeft">
        <div className="div-header single-header">
  <NavLink className="card-header single" to="/dashboard/setting">
    Settings
  </NavLink>
</div>


        <NavLink
          className={`headersForManuals ${updateCount === 0 ? "unactive" : ""}`}
          to={updateCount > 0 ? "/dashboard/UpdateManuals" : "#"}
          onClick={(e) => {
            if (updateCount === 0) e.preventDefault();
          }}
        >
          <span>Updates</span>

          {updateCount > 0 && (
            <span className="update-alert-count">{updateCount}</span>
          )}
        </NavLink>

        <NavLink to="#" className="headersForManuals" onClick={()=>{setIsHelpClicked(!isHelpClicked)}}>
          Help
        </NavLink>

        <NavLink className="headersForManuals" to="/dashboard/manuals/chat">
          What's new
        </NavLink>
        <NavLink className={`headersForManuals`} to="/dashboard/manuals/chat">
          Change Password
        </NavLink>
        <NavLink
  className="headersForManuals"
  to="#"
  onClick={(e) => {
    e.preventDefault();
    setIsAboutOpen(!isAboutOpen);
    setIsHelpClicked(false);
  }}
>
  About
</NavLink>


        <h5 className="card-header">App theme</h5>

        <div className="divDarkLight">
          <ThemeToggle />
          <button onClick={logout} className="logOutButton"><img src={logoutSvg} alt="" /> Logout</button>
        </div>
      </div>
      {isHelpClicked && <div className="manualsContainer" style={{height:'88vh'}}>
        <iframe
                src={'/EFB_Help_V2_050316.pdf#toolbar=0&navpanes=0&scrollbar=0'}
                width="100%"
                height="100%"
                style={{ border: "none" ,borderRadius:'8px'}}
                title="PDF preview"
              />
        </div>}
        {isAboutOpen && (
  <div className="manualsContainer" style={{height:'88vh', display:'flex', alignItems:'center', justifyContent:'center'}}>
    <div className="aboutBox">
      <h2>EFB Crew App</h2>
      <p>Version: 1.0.0</p>
      <p>Electronic Flight Bag for crew members.</p>
    </div>
  </div>
)}

      </PageWrapper>
    </>
  );
};

export default Setting;
