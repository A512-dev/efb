import { NavLink } from "react-router-dom";
import ThemeToggle from "../components/ThemeToggle";
import { useNotifications } from "../Context/NotificationContext";

const UpdateManuals = () => {
  const {
    updates = [],
    updateCount = 0,
    loading = false,
    markAsSeen,
    seenIds = []
  } = useNotifications();

  const handleUpdateClick = (item) => {
    markAsSeen(item.id);
  };

  return (
    <>
      <div className="manualsContainerLeft">
        <div className="div-header">
          <NavLink className="card-header" to="/dashboard/setting">
            Settings
          </NavLink>
        </div>

        <NavLink
          className="headersForManuals active"
          to="/dashboard/UpdateManuals"
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

      <div className="manualsContainer">
        
          <div className="manual-updates-header">
            <h2 className="manual-updates-title">Manual Updates</h2>
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
                    <div className="manual-update-action">
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
                      {item.created_at ?? "-"}
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
    </>
  );
};

export default UpdateManuals;
