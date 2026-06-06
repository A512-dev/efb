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
      <div className="manualsContainer">
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
    </PageWrapper>
  );
};

export default SignUp;
