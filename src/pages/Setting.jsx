import { NavLink } from "react-router-dom";
import ThemeToggle from "../components/ThemeToggle.jsx";
import { useNotifications } from "../Context/NotificationContext";

const Setting = () => {
  const { updateCount } = useNotifications();

  return (
    <>
      <div className="manualsContainerLeft">
        <div className="div-header">
          <NavLink className="card-header" to="/dashboard/setting">
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
