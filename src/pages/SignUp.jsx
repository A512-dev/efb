
// import PageWrapper from "../components/PageWrapper";
// import { useState, useEffect, useMemo } from "react";
// import { createPilotUser, getAllUsers } from "../services/apiService";

// const SignUp = () => {
//   const [formData, setFormData] = useState({
//     name: "",
//     email: "",
//     role: "pilot",
//   });

//   const [loading, setLoading] = useState(false);
// const [users, setUsers] = useState([]);

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
// useEffect(() => {
//   const loadUsers = async () => {
//     try {
//       const data = await getAllUsers();
//       setUsers(data);
//     } catch (err) {
//       console.error("Error loading users:", err);
//     }
//   };

//   loadUsers();
// }, []);
// const { p1Count, p2Count } = useMemo(() => {
//   const p1 = users.filter((u) => u.position === "P1").length;
//   const p2 = users.filter((u) => u.position === "P2").length;

//   return { p1Count: p1, p2Count: p2 };
// }, [users]);

// const fleetCounts = useMemo(() => {
//   const counts = {
//     A300_600: 0,
//     A320: 0,
//     A330: 0,
//     F100: 0,
//     ATR72_600: 0
//   };

//   const filtered =
//     fleetFilter === "all"
//       ? users
//       : users.filter((u) => u.aircraft_type === fleetFilter);

//   filtered.forEach((user) => {
//     if (counts[user.aircraft_type] !== undefined) {
//       counts[user.aircraft_type]++;
//     }
//   });

//   return counts;
// }, [users, fleetFilter]);

// console.log(users)
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
//         </div>
//       <div className="dashboard-grid">

//   <article className="dashboard-card">
//     <span>Total P1</span>
//     <strong>{p1Count}</strong>
//   </article>

//   <article className="dashboard-card">
//     <span>Total P2</span>
//     <strong>{p2Count}</strong>
//   </article>

// </div>

          
//         {/* ))} */}
//       <div className="signupContainer">
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
//       </div>
//       </section>
//     </PageWrapper>
//   );
// };

// export default SignUp;
import PageWrapper from "../components/PageWrapper";
import { useState, useEffect, useMemo } from "react";
import { createPilotUser, getAllUsers } from "../services/apiService";
import { createPortal } from "react-dom";

const SignUp = () => {
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    password: "",
    role: "pilot",
    position: "P2",
    aircraft_type: "A320",
  });

  const [errorModal, setErrorModal] = useState({
    open: false,
    message: "",
  });
  
  const [loading, setLoading] = useState(false);
  const [users, setUsers] = useState([]);
  const [fleetFilter, setFleetFilter] = useState("all");
  
  const [successModal, setSuccessModal] = useState({
    open: false,
    email: "",
  });

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleCreatePilot = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const email = formData.email;

      await createPilotUser(formData);

      setSuccessModal({
        open: true,
        email,
      });

      setFormData({
        name: "",
        email: "",
        password: "",
        role: "pilot",
        position: "P2",
        aircraft_type: "A320",
      });
    } catch (err) {
      console.error(err);

      if (err.response?.status === 409) {
        setErrorModal({
          open: true,
          message:
            "This user already exists.\n\nIf you want to recreate this user, please delete their profile from Crew Profile first.",
        });
      } else {
        setErrorModal({
          open: true,
          message: "Failed to create the user. Please try again.",
        });
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const loadUsers = async () => {
      try {
        const data = await getAllUsers();
        setUsers(data);
      } catch (err) {
        console.error("Error loading users:", err);
      }
    };

    loadUsers();
  }, []);

  const filteredUsers = useMemo(() => {
    if (fleetFilter === "all") return users;

    return users.filter((u) => u.aircraft_type === fleetFilter);
  }, [users, fleetFilter]);

  const { p1Count, p2Count } = useMemo(() => {
    const p1 = filteredUsers.filter((u) => u.position === "P1").length;
    const p2 = filteredUsers.filter((u) => u.position === "P2").length;

    return { p1Count: p1, p2Count: p2 };
  }, [filteredUsers]);

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
            <option value="A330">A330</option>
            <option value="A300_600">A300-600 / A310</option>
            <option value="A320">A320</option>
            <option value="F100">F100</option>
            <option value="ATR">ATR 72-600</option>
          </select>
        </div>

        <div className="dashboard-grid">
          <article className="dashboard-card">
            <span>Total Pilots</span>
            <strong>{filteredUsers.length}</strong>
          </article>

          <article className="dashboard-card">
            <span>P1</span>
            <strong>{p1Count}</strong>
          </article>

          <article className="dashboard-card">
            <span>P2</span>
            <strong>{p2Count}</strong>
          </article>
        </div>

        <div className="signupContainer">
          <h2>Create New User</h2>

          <form onSubmit={handleCreatePilot} className="create-user-form">
            <div className="form-group">
              <label>Name</label>
              <input
                type="text"
                name="name"
                placeholder="Enter pilot name"
                value={formData.name}
                onChange={handleChange}
                required
              />
            </div>

            <div className="form-group">
              <label>Email</label>
              <input
                type="email"
                name="email"
                placeholder="Enter email"
                value={formData.email}
                onChange={handleChange}
                required
              />
            </div>
            
            <div className="form-group">
              <label>Password</label>
              <input
                type="password"
                name="password"
                placeholder="Enter password"
                value={formData.password}
                onChange={handleChange}
                required
              />
            </div>

            <div className="form-group">
              <label>Role</label>
              <select name="role" value={formData.role} onChange={handleChange}>
                <option value="pilot">Pilot</option>
              </select>
            </div>
            
            <div className="form-group">
              <label>Position</label>
              <select name="position" value={formData.position} onChange={handleChange}>
                <option value="P1">P1 (Captain)</option>
                <option value="P2">P2 (First Officer)</option>
              </select>
            </div>
            
            <div className="form-group">
              <label>Aircraft Type</label>
              <select name="aircraft_type" value={formData.aircraft_type} onChange={handleChange}>
                <option value="A330">A330</option>
                <option value="A300_600">A300-600 / A310</option>
                <option value="A320">A320</option>
                <option value="F100">F100</option>
                <option value="ATR">ATR 72-600</option>
              </select>
            </div>

            <button type="submit" disabled={loading}>
              {loading ? "Creating..." : "Create User"}
            </button>
          </form>
        </div>
      </section>

      {createPortal(
        <>
          {successModal.open && (
            <div className="signup-modal-overlay">
              <div className="signup-modal-content">
                <h2>User Created Successfully</h2>
                <p>The user account has been created successfully.</p>
                <p>
                  <strong>Email:</strong> {successModal.email}
                </p>
                <button
                  className="signup-modal-button"
                  onClick={() =>
                    setSuccessModal({
                      open: false,
                      email: "",
                    })
                  }
                >
                  OK
                </button>
              </div>
            </div>
          )}

          {errorModal.open && (
            <div className="signup-modal-overlay">
              <div className="signup-modal-content">
                <h2 style={{ color: "#dc2626" }}>Unable to Create User</h2>
                <p
                  style={{
                    whiteSpace: "pre-line",
                    borderBottom: "1px solid red",
                    color: "#dc2626",
                  }}
                >
                  {errorModal.message}
                </p>
                <button
                  className="signup-modal-button"
                  onClick={() =>
                    setErrorModal({
                      open: false,
                      message: "",
                    })
                  }
                >
                  OK
                </button>
              </div>
            </div>
          )}
        </>,
        document.body
      )}
    </PageWrapper>
  );
};

export default SignUp;
