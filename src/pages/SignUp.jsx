import { useState } from "react";
import PageWrapper from "../components/PageWrapper";
import { createPilotUser } from "../services/apiService";

const SignUp = () => {
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    role: "pilot",
  });

  const [loading, setLoading] = useState(false);

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
      const newUser = await createPilotUser(formData);
      alert("User created: " + newUser.email);

      setFormData({
        name: "",
        email: "",
        role: "pilot",
      });
    } catch (err) {
      console.error(err);
      alert("ساخت کاربر جدید با خطا مواجه شد");
    } finally {
      setLoading(false);
    }
  };

  return (
    <PageWrapper>
      
      <section className="dashboard-panel">
        <h2 style={{padding:'10px 20px'}}>Crew Status</h2>
      <div className="dashboard-filters">
          {/* <input
            type="search"
            placeholder="Search reports"
            // value={filters.search}
            // onChange={(event) =>
            //   setFilters((current) => ({ ...current, search: event.target.value }))
            // }
          /> */}
          {/* <select
            // value={filters.status}
            // onChange={(event) =>
            //   setFilters((current) => ({ ...current, status: event.target.value }))
            // }
          >
            <option value="all">All statuses</option>
            <option value="SUBMITTED">Submitted</option>
            <option value="IN_REVIEW">In review</option>
            <option value="RETURNED_TO_SUBMITTER">Returned</option>
            <option value="RESUBMITTED">Resubmitted</option>
            <option value="APPROVED">Approved</option>
            <option value="CLOSED">Closed</option>
          </select> */}
          <select
            // value={filters.type}
            // onChange={(event) =>
            //   setFilters((current) => ({ ...current, type: event.target.value }))
            // }
          >
            <option className="optionSignUp" value="all">All Fleets</option>
            {/* {reportTypes.map((report) => ( */}
            <option>
                A330
              </option>
              <option>
                A300-600/310
              </option>
              <option>
                A320
              </option>
              <option>
                F100
              </option>
              <option>
                ATR 72-600
              </option>
            {/* // ))} */}
          </select>
        </div>
      <div className="dashboard-grid">
        
      {/* {statCards.map(([label, value]) => ( */}
          
          <article className="dashboard-card" key={'pilot'}>
            <span> Total P1: 34</span>
            <strong> {loading}</strong>
          </article>
          <article className="dashboard-card" key={'pilot'}>
            <span>Total P2: 9</span>
            <strong> {loading}</strong>
          </article>
          
          </div>
          
        {/* ))} */}
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
            <label>Role</label>
            <select
              name="role"
              value={formData.role}
              onChange={handleChange}
            >
              <option value="pilot">Pilot</option>
              
            </select>
          </div>

          <button type="submit" disabled={loading}>
            {loading ? "Creating..." : "Create User"}
          </button>
        </form>
      </div>
      </section>
    </PageWrapper>
  );
};

export default SignUp;
