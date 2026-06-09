import { NavLink } from "react-router-dom";
import ThemeToggle from "../components/ThemeToggle";
import { useNotifications } from "../Context/NotificationContext";
import { useAuth } from "../auth/useAuth";
import logoutSvg from '../assets/icons/Power-Button--Streamline-Ultimate.svg'
import PageWrapper from "../components/PageWrapper";


import { useState } from "react";

const UpdateManuals = () => {
  const {
    updates = [],
    updateCount = 0,
    loading = false,
    markAsSeen,
    markAllAsSeen,
    seenIds = [],

  } = useNotifications();
const { logout } = useAuth();
  const handleUpdateClick = (item) => {
  if (seenIds.includes(String(item.id))) return;
  markAsSeen(item.id);
};


    
const handleMarkAllAsRead = () => {
  markAllAsSeen();
};
const [isHelpClicked,setIsHelpClicked]= useState(false)
const [isAboutOpen, setIsAboutOpen] = useState(false);

  const formatDate = (dateString) => {
  const date = new Date(dateString);

  return date.toLocaleString("fa-IR-u-nu-latn", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  });
};


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
          className="headersForManuals active"
          to="/dashboard/UpdateManuals"
        >
          <span className={ ` ${ !isHelpClicked ?'spanUpdate' : ''}`} onClick={()=>{setIsHelpClicked(false)}}>Updates</span>
          {updateCount > 0 && (
            <span className="update-alert-count">{updateCount}</span>
          )}
        </NavLink>

        <NavLink to="#" className="headersForManuals" onClick={()=>{setIsHelpClicked(!isHelpClicked)}}>
          <span className={ ` ${ isHelpClicked ?'spanUpdate' : ''}`}> Help </span>
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
    <div className={`${isHelpClicked ? 'hideManualsContainer':  'manualsContainer'}`}>
        
        <div className="manual-updates-panel">
          <div className="manual-updates-header">
            <h2 className="manual-updates-title">Manual Updates</h2>
            <button
  className="manual-update-readall-btn"
  onClick={handleMarkAllAsRead}
  disabled={updateCount === 0}
>
  Update All Documents
</button>

          </div>

          {loading && updates.length === 0 && (
            <div className="manual-updates-state">Loading...</div>
          )}

          {!loading && updates.length === 0 && (
            <div className="manual-updates-state">No updates found.</div>
          )}

          <div className="manual-updates-list">
            {updates.map((item) => {
              const isSeen = seenIds.includes(String(item.id));

              return (
                <div
                  key={item.id}
                  className={`manual-update-card ${
                    isSeen ? "seen" : "unseen"
                  }`}
                  onClick={() => handleUpdateClick(item)}
                >
                  <div className="manual-update-top">
                    <div className="manual-update-title">
                      {item.title || "Untitled manual"}
                    </div>
                    <div
  className={`manual-update-action action-${(item.action || "updated").toLowerCase()}`}
>
  {item.action || "updated"}
</div>

                  </div>

                  <div className="manual-update-meta">
                    <div>
                      <strong>Manual ID:</strong>{" "}
                      {item.manual_id ?? "-"}
                    </div>
                    <div>
                      <strong>Date:</strong>{" "}
                      {item.created_at ? formatDate(item.created_at) : "-"}
                    </div>
                  </div>

                  <div className="manual-update-note">
                    <strong>Note:</strong> {item.note || "-"}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
      </PageWrapper>
    </>
  );
};

export default UpdateManuals;
