import { NavLink } from "react-router-dom";
import ThemeToggle from "../components/ThemeToggle.jsx";
import { useNotifications } from "../Context/NotificationContext";
import { useAuth } from "../auth/useAuth.js";
import logoutSvg from "../assets/icons/Power-Button--Streamline-Ultimate.svg";
import PageWrapper from "../components/PageWrapper.jsx";
import { Construction } from "lucide-react";
import { useState, useEffect } from "react";
import { getCurrentUser } from "../services/apiService";
const Setting = () => {
  const { updateCount } = useNotifications();
  const { logout } = useAuth();
const [currentUser, setCurrentUser] = useState(null);
const isAdmin = currentUser?.role === "admin";
const [activeTab, setActiveTab] = useState("about");

useEffect(() => {
  const loadUser = async () => {
    try {
      const user = await getCurrentUser();
      setCurrentUser(user);
    } catch (err) {
      console.error("Failed to load current user:", err);
    }
  };

  loadUser();
}, []);



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
            className="headersForManuals"
            to="#"
            onClick={(e) => {
              e.preventDefault();
              setActiveTab("about");
            }}
          >
            About
          </NavLink>

          {!isAdmin && (
  <NavLink
    className={`headersForManuals ${
      updateCount === 0 ? "unactive" : ""
    }`}
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
)}

          <NavLink
            to="#"
            className="headersForManuals"
            onClick={(e) => {
              e.preventDefault();
              setActiveTab("help");
            }}
          >
            Help
          </NavLink>

          <NavLink
  to="#"
  className="headersForManuals"
  onClick={(e) => {
    e.preventDefault();
    setActiveTab("whatsnew");
  }}
>
  What's new
</NavLink>

<NavLink
  to="#"
  className="headersForManuals"
  onClick={(e) => {
    e.preventDefault();
    setActiveTab("password");
  }}
>
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
          <div className="manualsContainer" style={{ height: "88vh" }}>
            <div
              style={{
                width: "100%",
                height: "100%",
                overflow: "hidden",
                borderRadius: "8px",
              }}
            >
              <iframe
                src="/EFB_Help_V2_050316.pdf"
                style={{
                  border: "none",
                  width: "100%",
                  height: "120%",
                  marginTop: "-60px",
                }}
                title="PDF preview"
              />
            </div>
          </div>
        )}

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
         <button
  className="versionButton"
  // onClick={() => navigator.clipboard.writeText("1.0.0")}
>
  
  <span>Update Version</span>
</button>
              <p>© All rights reserved by SkyTechSharif</p>
            </div>
          </div>
        )}
        {(activeTab === "whatsnew" ||
  activeTab === "password") && (
  <div className="manualsContainer">
    <div className="comingSoonBox">
      <h2><Construction size={48} strokeWidth={1.8} color="var(--accent)" /> Coming Soon</h2>

      <p>
        This feature is currently under development and
        will be available in a future update.
      </p>
    </div>
  </div>
)}
      </PageWrapper>
    </>
  );
};

export default Setting;
