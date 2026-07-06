import { NavLink } from "react-router-dom";
import ThemeToggle from "../components/ThemeToggle";
import { useNotifications } from "../Context/NotificationContext";
import { useAuth } from "../auth/useAuth";
import logoutSvg from "../assets/icons/Power-Button--Streamline-Ultimate.svg";
import PageWrapper from "../components/PageWrapper";

import { useEffect, useState } from "react";
import { getManuals } from "../services/apiService";
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
const [manuals, setManuals] = useState([]);
  const [activeTab, setActiveTab] = useState("updates"); 
const [updatesTab, setUpdatesTab] = useState("unread"); 
useEffect(() => {
  const loadManuals = async () => {
    try {
      const data = await getManuals();
      setManuals(data);
    } catch (err) {
      console.error(err);
    }
  };

  loadManuals();
}, []);
  const handleUpdateClick = (item) => {
    if (seenIds.includes(String(item.id))) return;
    markAsSeen(item.id);
  };

  const handleMarkAllAsRead = () => {
    markAllAsSeen();
  };

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
const unreadUpdates = updates.filter(
  (item) => !seenIds.includes(String(item.id))
);

const readUpdates = updates.filter(
  (item) => seenIds.includes(String(item.id))
);

  return (
    <PageWrapper>
      <div className="manualsContainerLeft">
        <div className="div-header single-header">
          <NavLink className="card-header single" to="/dashboard/setting">
            Settings
          </NavLink>
        </div>
<NavLink
          className="headersForManuals"
          to="#"
          onClick={(e) => {
            e.preventDefault();
            setActiveTab("about");
          }}
        >
          About
        </NavLink>
        <NavLink
          className="headersForManuals"
          to="#"
          onClick={(e) => {
            e.preventDefault();
            setActiveTab("updates");
          }}
        >
          <span className={activeTab === "updates" ? "spanUpdate" : ""}>
            Updates
          </span>

          {updateCount > 0 && (
            <span className="update-alert-count">{updateCount}</span>
          )}
        </NavLink>

        <NavLink
          to="#"
          className="headersForManuals"
          onClick={(e) => {
            e.preventDefault();
            setActiveTab("help");
          }}
        >
          <span className={activeTab === "help" ? "spanUpdate" : ""}>
            Help
          </span>
        </NavLink>

        <NavLink className="headersForManuals" to="/dashboard/manuals/chat">
          What's new
        </NavLink>

        <NavLink className="headersForManuals" to="/dashboard/manuals/chat">
          Change Password
        </NavLink>

        

        <h5 className="card-header">App theme</h5>

        <div className="divDarkLight">
          <ThemeToggle />
          <button onClick={logout} className="logOutButton">
            <img src={logoutSvg} alt="" /> Logout
          </button>
        </div>
      </div>

      {activeTab === "help" && (
        <div className="manualsContainer" style={{height:'88vh'}}>
        <div style={{ width: "100%", height: "100%", overflow: "hidden", borderRadius: "8px" }}>
  <iframe
    src="/EFB_Help_V2_050316.pdf"
    style={{
      border: "none",
      width: "100%",
      height: "120%",
      marginTop: "-60px"
    }}
    title="PDF preview"
  />
</div>


        </div>)}
      

      {activeTab === "about" && (
        <div
          className="manualsContainer"
          style={{
            height: "88vh",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          <div className="aboutBox">
            <h1>produced by SkyTechSharif</h1>
            <h2>EFB Crew App</h2>
            <p>Version: 1.0.0</p>
            <p>© All rights reserved by SkyTechSharif</p>
          </div>
        </div>
      )}

      {activeTab === "updates" && (
        <div className="manualsContainer">
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

<div className="updates-tabs">
  <button
    className={`manual-update-readall-btn ${updatesTab === "unread" ? "active" : ""}`}
    onClick={() => setUpdatesTab("unread")}
  >
    Unread
  </button>

  <button
    className={`manual-update-readall-btn ${updatesTab === "read" ? "active" : ""}`}
    onClick={() => setUpdatesTab("read")}
  >
    Read
  </button>
</div>


            {loading && updates.length === 0 && (
              <div className="manual-updates-state">Loading...</div>
            )}

            {!loading && updates.length === 0 && (
              <div className="manual-updates-state">No updates found.</div>
            )}

            <div className="manual-updates-list">
              {(updatesTab === "unread" ? unreadUpdates : readUpdates).map((item) => {

                const isSeen = seenIds.includes(String(item.id));
const manual = manuals.find((m) => m.id === item.manual_id);
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
                <p style={{ fontSize: "12px", color: "#666" }}>
  {manual?.original_filename} |{" "}
  
</p>
                      <div
                        className={`manual-update-action action-${(
                          item.action || "updated"
                        ).toLowerCase()}`}
                      >
                        {item.action || "updated"}
                      </div>
                    </div>

                    <div className="manual-update-meta">
                      <div>
                        <strong>Manual ID:</strong> {item.manual_id ?? "-"}
                      </div>

                      <div>
                        <strong>Date:</strong>{" "}
                        {item.created_at
                          ? formatDate(item.created_at)
                          : "-"}
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
      )}
    </PageWrapper>
  );
};

export default UpdateManuals;
