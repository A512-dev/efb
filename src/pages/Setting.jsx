import { NavLink } from "react-router-dom";
import ThemeToggle from "../components/ThemeToggle.jsx";
import { useState } from "react";

const Setting = () => {
  const [isFull, setIsFull] = useState(false);

  return (
    <>
      <div className="manualsContainerLeft">
        <div className="div-header">
          <NavLink className="card-header" to="/dashboard/setting">
            Settings
          </NavLink>
        </div>

        <NavLink
          className={`headersForManuals  ${isFull===false ? "unactive" : ""}`}
          to={isFull ? "/dashboard/UpdateManuals" : "#"}
          onClick={(e) => {
            if (!isFull) e.preventDefault();
          }}
        >
          Updates
        </NavLink>

        <NavLink to="/dashboard/manuals" className="headersForManuals">
          Help
        </NavLink>

        <NavLink className="headersForManuals" to="/dashboard/manuals/chat">
          What's new
        </NavLink>

        

        <h5 className="card-header">App theme</h5>

        <div className="divDarkLight">
          <ThemeToggle />
        </div>
      </div>
    </>
  );
};

export default Setting;
