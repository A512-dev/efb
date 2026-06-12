import { NavLink } from "react-router-dom";
import ThemeToggle from "../components/ThemeToggle.jsx";
import { useNotifications } from "../Context/NotificationContext";
import { useAuth } from "../auth/useAuth.js";
import logoutSvg from "../assets/icons/Power-Button--Streamline-Ultimate.svg";
import PageWrapper from "../components/PageWrapper.jsx";
import { useState } from "react";

const Setting = () => {
  const { updateCount } = useNotifications();
  const { logout } = useAuth();

  const [activeTab, setActiveTab] = useState(null); // help | about | null

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
              <p>© All rights reserved by SkyTechSharif</p>
            </div>
          </div>
        )}
      </PageWrapper>
    </>
  );
};

export default Setting;
