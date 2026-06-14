import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useCurrentUser } from "../hooks/useCurrentUser";
import {
  updateProfile,
  uploadProfilePicture,
  downloadMyProfilePicture
} from "../services/apiService";
import PageWrapper from "../components/PageWrapper";

const EditProfile = () => {
  const { user, refreshUser, loading } = useCurrentUser();

  const navigate = useNavigate();

  const [employeeNo, setEmployeeNo] = useState("");
const [position, setPosition] = useState("");
const [aircraftType, setAircraftType] = useState("");
const [medicalExpire, setMedicalExpire] = useState("");
const [passportExpire, setPassportExpire] = useState("");
const [licenseExpire, setLicenseExpire] = useState("");


  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    const loadCurrentImg = async () => {
      try {
        const blob = await downloadMyProfilePicture();
        if (blob) {
          const url = URL.createObjectURL(blob);
          setPreviewUrl(url);
        }
      } catch (e) {
        console.log("No existing image");
      }
    };

    loadCurrentImg();
  }, []);
  

  useEffect(() => {
  if (!user) return;

  setEmployeeNo(user.employee_no || "");
  setPosition(user.position || "");
  setAircraftType(user.aircraft_type || "");

  setMedicalExpire(user.medical_expires_at?.split("T")[0] || "");
  setPassportExpire(user.passport_expires_at?.split("T")[0] || "");
  setLicenseExpire(user.license_expires_at?.split("T")[0] || "");
}, [user]);



  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedFile(file);
      setPreviewUrl(URL.createObjectURL(file));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      if (selectedFile) {
        await uploadProfilePicture(selectedFile);
      }

      await updateProfile({
        employee_no: employeeNo,
        position: position,
        aircraft_type: aircraftType,
        medical_expires_at: medicalExpire
          ? new Date(medicalExpire).toISOString()
          : null,
        passport_expires_at: passportExpire
          ? new Date(passportExpire).toISOString()
          : null,
        license_expires_at: licenseExpire
          ? new Date(licenseExpire).toISOString()
          : null
      });

      await refreshUser();

      alert("Profile updated successfully!");
      navigate("/dashboard/profile");
    } catch (error) {
      console.error("Update failed:", error);
      alert("Failed to update profile.");
    } finally {
      setIsSubmitting(false);
    }
  };
if (loading) {
  return (
    <PageWrapper>
      <div style={{ padding: 40 }}>Loading profile...</div>
    </PageWrapper>
  );
}

if (!user) {
  return (
    <PageWrapper>
      <div style={{ padding: 40 }}>Not authenticated</div>
    </PageWrapper>
  );
}


  return (
   <PageWrapper>
  <div className="crew-main-card">

    <div className="edit-profile-card">
      
      <div className="profile-upload-section">
        <div className="preview-circle">
          <img src={previewUrl || "/default-avatar.png"} alt="Preview" />
        </div>

        <input
          type="file"
          accept="image/*"
          onChange={handleFileChange}
          id="fileInput"
          hidden
        />

        <label htmlFor="fileInput" className="upload-label">
          Change Photo
        </label>
      </div>

      <form onSubmit={handleSubmit} className="form-section">

        <h2>Edit Profile</h2>

        <div className="form-grid">

          <div className="input-group">
            <label>Employee No</label>
            <input
              type="text"
              value={employeeNo}
              onChange={(e) => setEmployeeNo(e.target.value)}
            />
          </div>

          <div className="input-group">
            <label>Position</label>
            <select className="selectProfile"
  value={position}
  onChange={(e) => setPosition(e.target.value)}
>
  <option value="">Select Position</option>
  <option value="P1">P1</option>
  <option value="P2">P2</option>
</select>

          </div>

          <div className="input-group">
            <label>Aircraft Type</label>
            <select className="selectProfile"
  value={aircraftType}
  
  onChange={(e) => setAircraftType(e.target.value)}
>
  <option value="">Select Aircraft</option>
  <option value="A300_600">A300-600/310</option>
  <option value="A310">A320</option>
</select>

          </div>

          <div className="input-group">
            <label>Medical Expiry</label>
            <input
              type="date"
              value={medicalExpire}
              onChange={(e) => setMedicalExpire(e.target.value)}
            />
          </div>

          <div className="input-group">
            <label>Passport Expiry</label>
            <input
              type="date"
              value={passportExpire}
              onChange={(e) => setPassportExpire(e.target.value)}
            />
          </div>

          <div className="input-group">
            <label>License Expiry</label>
            <input
              type="date"
              value={licenseExpire}
              onChange={(e) => setLicenseExpire(e.target.value)}
            />
          </div>

        </div>

        <div className="edit-actions">
          <button
            type="button"
            onClick={() => navigate("/dashboard/profile")}
            className="cancel-btn"
          >
            Cancel
          </button>

          <button
            type="submit"
            disabled={isSubmitting}
            className="save-btn"
          >
            {isSubmitting ? "Saving..." : "Save Changes"}
          </button>
        </div>

      </form>
    </div>
  </div>
</PageWrapper>

  );
};

export default EditProfile;
