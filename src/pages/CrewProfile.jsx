// import { useState } from "react";
// import PageWrapper from "../components/PageWrapper";
// import { createPilotUser } from "../services/apiService";

// const CrewProfile = () => {
//   const [formData, setFormData] = useState({
//     name: "",
//     email: "",
//     role: "pilot",
//   });

//   const [loading, setLoading] = useState(false);

//   const handleChange = (e) => {
//     setFormData({
//       ...formData,
//       [e.target.name]: e.target.value,
//     });
//   };

//   const handleCreatePilot = async (e) => {
//     e.preventDefault();
//     setLoading(true);

//     try {
//       const newUser = await createPilotUser(formData);
//       alert("User created: " + newUser.email);

//       setFormData({
//         name: "",
//         email: "",
//         role: "pilot",
//       });
//     } catch (err) {
//       console.error(err);
//       alert("ساخت کاربر جدید با خطا مواجه شد");
//     } finally {
//       setLoading(false);
//     }
//   };

//   return (
//     <PageWrapper>
      
//       <section className="dashboard-panel">
//         <h2 style={{padding:'10px 20px'}}>Crew Status</h2>
//       <div className="dashboard-filters">
//           {/* <input
//             type="search"
//             placeholder="Search reports"
//             // value={filters.search}
//             // onChange={(event) =>
//             //   setFilters((current) => ({ ...current, search: event.target.value }))
//             // }
//           /> */}
//           {/* <select
//             // value={filters.status}
//             // onChange={(event) =>
//             //   setFilters((current) => ({ ...current, status: event.target.value }))
//             // }
//           >
//             <option value="all">All statuses</option>
//             <option value="SUBMITTED">Submitted</option>
//             <option value="IN_REVIEW">In review</option>
//             <option value="RETURNED_TO_SUBMITTER">Returned</option>
//             <option value="RESUBMITTED">Resubmitted</option>
//             <option value="APPROVED">Approved</option>
//             <option value="CLOSED">Closed</option>
//           </select> */}
//           <select
//             // value={filters.type}
//             // onChange={(event) =>
//             //   setFilters((current) => ({ ...current, type: event.target.value }))
//             // }
//           >
//             <option className="optionSignUp" value="all">All Fleets</option>
//             {/* {reportTypes.map((report) => ( */}
//             <option>
//                 A330
//               </option>
//               <option>
//                 A300-600/310
//               </option>
//               <option>
//                 A320
//               </option>
//               <option>
//                 F100
//               </option>
//               <option>
//                 ATR 72-600
//               </option>
//             {/* // ))} */}
//           </select>
//           <select
//             // value={filters.type}
//             // onChange={(event) =>
//             //   setFilters((current) => ({ ...current, type: event.target.value }))
//             // }
//           >
//             <option className="optionSignUp" value="all">All Crew</option>
//             {/* {reportTypes.map((report) => ( */}
//             <option>
//                 P1
//               </option>
//               <option>
//                 P2
//               </option>
              
//             {/* // ))} */}
//           </select>
//         </div>
//       <div className="dashboard-grid">
        
//       {/* {statCards.map(([label, value]) => ( */}
          
//           <article className="dashboard-card" key={'pilot'}>
//             <span> Total P1: 34</span>
//             <strong> {loading}</strong>
//           </article>
//           <article className="dashboard-card" key={'pilot'}>
//             <span>Total P2: 9</span>
//             <strong> {loading}</strong>
//           </article>
          
//           </div>
          
//         {/* ))} */}
//       {/* <div className="signupContainer">
//         <h2>Create New User</h2>

//         <form onSubmit={handleCreatePilot} className="create-user-form">
//           <div className="form-group">
//             <label>Name</label>
//             <input
//               type="text"
//               name="name"
//               placeholder="Enter pilot name"
//               value={formData.name}
//               onChange={handleChange}
//               required
//             />
//           </div>

//           <div className="form-group">
//             <label>Email</label>
//             <input
//               type="email"
//               name="email"
//               placeholder="Enter email"
//               value={formData.email}
//               onChange={handleChange}
//               required
//             />
//           </div>

//           <div className="form-group">
//             <label>Role</label>
//             <select
//               name="role"
//               value={formData.role}
//               onChange={handleChange}
//             >
//               <option value="pilot">Pilot</option>
              
//             </select>
//           </div>

//           <button type="submit" disabled={loading}>
//             {loading ? "Creating..." : "Create User"}
//           </button>
//         </form>
//       </div> */}
//       </section>
//     </PageWrapper>
//   );
// };

// export default CrewProfile;

// import { useState } from "react";
// import PageWrapper from "../components/PageWrapper";
// import cardImg from "../assets/icons/2d3ae130-4dab-480a-9f81-1612825326e5.webp";

// const CrewProfile = () => {

//   const pilots = [
//     { id: 1, name: "Capt. Ali Rahimi", emp: "EP1001", type: "P1", fleet: "A330", medical: "15 Dec 2026", passport: "20 May 2027" },
//     { id: 2, name: "Capt. Reza Mohammadi", emp: "EP1002", type: "P1", fleet: "A320", medical: "02 Feb 2026", passport: "14 Aug 2027" },
//     { id: 3, name: "F.O. Mehdi Karimi", emp: "EP2001", type: "P2", fleet: "ATR 72-600", medical: "11 Jan 2026", passport: "10 Oct 2026" },
//     { id: 4, name: "F.O. Arman Hashemi", emp: "EP2002", type: "P2", fleet: "F100", medical: "05 Jun 2026", passport: "18 Sep 2026" },
//     { id: 5, name: "Capt. Sina Ahmadi", emp: "EP1003", type: "P1", fleet: "A300-600/310", medical: "28 Mar 2027", passport: "02 Dec 2027" },
//   ];

//   const [selectedPilot, setSelectedPilot] = useState(null);
//   const [crewType, setCrewType] = useState("all");

//   const filteredPilots =
//     crewType === "all"
//       ? pilots
//       : pilots.filter((p) => p.type === crewType);

//   return (
//     <PageWrapper>
//       <section className="dashboard-panel" style={{overflowY:'auto'}}>
//         <h2 style={{ padding: "10px 20px" }}>Crew Profile</h2>

//         <div className="dashboard-filters">

//           <select>
//             <option value="all">All Fleets</option>
//             <option>A330</option>
//             <option>A300-600/310</option>
//             <option>A320</option>
//             <option>F100</option>
//             <option>ATR 72-600</option>
//           </select>

//           <select
//             value={crewType}
//             onChange={(e) => setCrewType(e.target.value)}
//           >
//             <option value="all">All Crew</option>
//             <option value="P1">P1</option>
//             <option value="P2">P2</option>
//           </select>

//         </div>

//         {/* لیست اسامی */}
//         <div className="dashboard-grid">
//           {filteredPilots.map((pilot) => (
//             <article
//               key={pilot.id}
//               className="dashboard-card"
//               style={{ cursor: "pointer" }}
//               onClick={() => setSelectedPilot(pilot)}
//             >
//               <span>{pilot.name}</span>
//               <strong>{pilot.type}</strong>
//             </article>
//           ))}
//         </div>

//         {/* کارت پروفایل */}
//         {selectedPilot && (
//           <div className="crew-page-wrapper">
//             <div className="crew-main-card">

//               <div className="crew-left-section">
//                 <div className="id-card-container" style={{ position: "relative" }}>
//                   <img src={cardImg} className="crew-card-base" alt="ID Card" />

//                   <div
//                     className="user-overlay-photo"
//                     style={{
//                       background: "#ccc",
//                       display: "flex",
//                       alignItems: "center",
//                       justifyContent: "center",
//                     }}
//                   >
//                     PHOTO
//                   </div>
//                 </div>
//               </div>

//               <div className="crew-right-section">
//                 <div className="crew-header">
//                   <h2>{selectedPilot.name}</h2>
//                 </div>

//                 <div className="crew-info-grid">
//                   <div className="crew-field">
//                     <label>EMP No</label>
//                     <p>{selectedPilot.emp}</p>
//                   </div>

//                   <div className="crew-field">
//                     <label>POSITION</label>
//                     <p>{selectedPilot.type}</p>
//                   </div>

//                   <div className="crew-field-last">
//                     <label>Type</label>
//                     <p>{selectedPilot.fleet}</p>
//                   </div>
//                 </div>

//                 <div className="crew-exp-section">
//                   <div className="expiry-item expire-green">
//                     <span>Medical</span>
//                     <strong>{selectedPilot.medical}</strong>
//                   </div>

//                   <div className="expiry-item expire-green">
//                     <span>Passport</span>
//                     <strong>{selectedPilot.passport}</strong>
//                   </div>
//                 </div>
//               </div>

//             </div>
//           </div>
//         )}
//       </section>
//     </PageWrapper>
//   );
// };

// export default CrewProfile;
import { useEffect, useMemo, useState } from "react";
import PageWrapper from "../components/PageWrapper";
import {
  getAllUsers,
  downloadUserProfilePicture,
  deleteUser,
  getUserManualReads,
} from "../services/apiService";
import CrewCard from "../components/CrewCard";
import crossMarkIcon from "../assets/icons/Delete-1--Streamline-Sharp.svg";
import { useManuals } from "../hooks/useManuals";
import { getAllManualReads } from "../services/apiService";

const CrewProfile = () => {
  const [users, setUsers] = useState([]);
  const [selectedPilot, setSelectedPilot] = useState(null);
  const [crewType, setCrewType] = useState("all");
  const [fleetFilter, setFleetFilter] = useState("all");
  const [loading, setLoading] = useState(true);
  const [profileImage, setProfileImage] = useState(null);
  const [userReads, setUserReads] = useState([]);
  const [showReadsModal, setShowReadsModal] = useState(false);

  const { manuals } = useManuals(null);

  const getManualTitle = (item) => {
    const manualId = item.manual_id || item.manualId || item.manual?.id;

    if (item.manual?.title) return item.manual.title;

    const manual = manuals.find(
      (m) => String(m.id) === String(manualId)
    );

    return manual?.title || `Manual #${manualId}`;
  };


  useEffect(() => {
    const loadUsers = async () => {
      try {
        const data = await getAllUsers();
        setUsers(data);
      } catch (err) {
        console.error("Error loading users:", err);
      } finally {
        setLoading(false);
      }
    };

    loadUsers();
  }, []);

  const pilots = useMemo(() => {
    return users.filter(
      (user) => user.position === "P1" || user.position === "P2"
    );
  }, [users]);

  const aircraftLabels = {
    A300_600: "A300-600 / A310",
    A320: "A320",
  };

  const fleetOptions = useMemo(() => {
    const fleets = pilots.map((p) => p.aircraft_type).filter(Boolean);
    return [...new Set(fleets)];
  }, [pilots]);
useEffect(() => {
  if (!selectedPilot) return;

  const loadReads = async () => {
    try {
      const userId = selectedPilot.id || selectedPilot.user_id;
      const data = await getAllManualReads();
      const items = Array.isArray(data) ? data : data?.items || [];

      const filtered = items.filter(
        (r) => String(r.user_id) === String(userId)
      );

      setUserReads(filtered);
    } catch (err) {
      console.error("Error loading user reads:", err);
    }
  };

  loadReads();
}, [selectedPilot]);

  useEffect(() => {
    if (!selectedPilot) return;

    setProfileImage(null);

    let objectUrl;

    const loadImage = async () => {
      try {
        const userId = selectedPilot.id || selectedPilot.user_id;
        const blob = await downloadUserProfilePicture(userId);

        if (blob) {
          objectUrl = URL.createObjectURL(blob);
          setProfileImage(objectUrl);
        }
      } catch (err) {
        console.error("Image load error:", err);
      }
    };

    loadImage();

    return () => {
      if (objectUrl) URL.revokeObjectURL(objectUrl);
    };
  }, [selectedPilot]);

  const filteredPilots = useMemo(() => {
    return pilots.filter((pilot) => {
      const matchType =
        crewType === "all" ? true : pilot.position === crewType;

      const matchFleet =
        fleetFilter === "all" ? true : pilot.aircraft_type === fleetFilter;

      return matchType && matchFleet;
    });
  }, [pilots, crewType, fleetFilter]);

  const handleDeleteUser = async () => {
    if (!selectedPilot) return;

    const confirmDelete = window.confirm(
      "Are you sure you want to delete this user?"
    );
    if (!confirmDelete) return;

    try {
      const userId = selectedPilot.id || selectedPilot.user_id;

      await deleteUser(userId);

      setUsers((prev) =>
        prev.filter((u) => (u.id || u.user_id) !== userId)
      );

      setSelectedPilot(null);
    } catch (err) {
      console.error("Delete error:", err);
      alert("Failed to delete user");
    }
  };

  return (
    <PageWrapper>
      <section className="dashboard-panel">
        <h2 style={{ padding: "10px 20px" }}>Crew Status</h2>

        <div className="dashboard-filters">
          <select
            value={fleetFilter}
            onChange={(e) => setFleetFilter(e.target.value)}
          >
            <option value="all">All Fleets</option>

            {fleetOptions.map((fleet) => (
              <option key={fleet} value={fleet}>
                {aircraftLabels[fleet] || fleet}
              </option>
            ))}
          </select>

          <select
            value={crewType}
            onChange={(e) => setCrewType(e.target.value)}
          >
            <option value="all">All Crew</option>
            <option value="P1">P1</option>
            <option value="P2">P2</option>
          </select>
        </div>

        {loading && <p style={{ padding: "20px" }}>Loading crew...</p>}

        {!loading && (
          <div className="dashboard-grid">
            {filteredPilots.map((pilot) => (
              <article
                key={pilot.id || pilot.user_id}
                className="dashboard-card"
                style={{ cursor: "pointer" }}
                onClick={() => setSelectedPilot(pilot)}
              >
                <span>{pilot.name}</span>
                <strong>{pilot.position}</strong>
              </article>
            ))}
          </div>
        )}

        {selectedPilot && (
          <div
            className="modal-overlay"
            onClick={() => setSelectedPilot(null)}
          >
            <div
              className="modal-content"
              onClick={(e) => e.stopPropagation()}
            >
              <button
                className="modal-close"
                onClick={() => setSelectedPilot(null)}
              >
                <img src={crossMarkIcon} alt="" />
              </button>

              <CrewCard
                user={selectedPilot}
                profileImage={profileImage}
              />

              <button
                className="viewReadsBtn"
                onClick={() => setShowReadsModal(true)}
              >
                View Read Manuals
              </button>
            </div>

            <button
              onClick={handleDeleteUser}
              className="deleteBtn deleteProfile"
            >
              Delete
            </button>
          </div>
        )}

        {showReadsModal && (
          <div
            className="modal-overlay"
            onClick={() => setShowReadsModal(false)}
          >
            <div
              className="modal-content"
              onClick={(e) => e.stopPropagation()}
            >
              <button
                className="modal-close"
                onClick={() => setShowReadsModal(false)}
              >
                <img src={crossMarkIcon} alt="" />
              </button>

              <h3 style={{ marginBottom: "12px" }}>
                {selectedPilot?.name} — Read Manuals
              </h3>

              {userReads.length === 0 ? (
                <p>No manuals read</p>
              ) : (
                <div className="adminReadList">
                  {userReads.map((r) => (
                    <div
                      key={r.id || r.manual_id}
                      className="adminReadRow"
                    >
                      <span>{getManualTitle(r)}</span>

                      {r.read_at && (
                        <small>
                          {new Date(r.read_at).toLocaleDateString()}
                        </small>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}
      </section>
    </PageWrapper>
  );
};

export default CrewProfile;
