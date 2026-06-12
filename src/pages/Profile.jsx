import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useCurrentUser } from "../hooks/useCurrentUser";
import { downloadMyProfilePicture } from "../services/apiService";
import PageWrapper from "../components/PageWrapper";
import cardImg from "../assets/icons/2d3ae130-4dab-480a-9f81-1612825326e5.webp";
import crewProfileSvg from "../assets/icons/Following-1--Streamline-Ultimate.svg";

const Profile = () => {
  const { user, loading } = useCurrentUser();
  const [profileImage, setProfileImage] = useState(null);

  const calcRemainingDays = (date) => {
    if (!date) return null;
    const now = new Date();
    const exp = new Date(date);
    const diff = exp - now;
    return Math.ceil(diff / (1000 * 60 * 60 * 24));
  };

  const formatDate = (date) => {
    if (!date) return "-";
    return new Date(date).toLocaleDateString("en-GB", {
      day: "2-digit",
      month: "short",
      year: "numeric"
    });
  };

  useEffect(() => {
    let objectUrl;

    const loadProfileImage = async () => {
      try {
        const blob = await downloadMyProfilePicture();
        if (blob) {
          objectUrl = URL.createObjectURL(blob);
          setProfileImage(objectUrl);
        }
      } catch (err) {
        console.error("Error loading profile picture:", err);
      }
    };

    if (user) loadProfileImage();

    return () => {
      if (objectUrl) URL.revokeObjectURL(objectUrl);
    };
  }, [user]);

  if (loading) return <div>Loading...</div>;
  if (!user) return <div>Not authenticated</div>;

  const medicalRemaining = calcRemainingDays(user.medical_expires_at);
  const passportRemaining = calcRemainingDays(user.passport_expires_at);
  const licenseRemaining = calcRemainingDays(user.license_expires_at);
const getExpiryClass = (days) => {
  if (days === null) return "";
  if (days <= 10) return "expire-red";
  if (days <= 30) return "expire-yellow";
  return "expire-green";
};


  return (
    <PageWrapper>
      <div className="crew-page-wrapper">
        <div className="crew-main-card">

         
<div className="crew-left-section">
  <div className="id-card-container" style={{ position: 'relative' }}>
    
    <img src={cardImg} className="crew-card-base" alt="ID Card Base" />
    
    
    {profileImage && (
      <img 
        src={profileImage} 
        className="user-overlay-photo" 
        alt="User Profile" 
      />
    )}

    
  </div>
</div>


          <div className="crew-right-section">
            <div className="crew-header">
              <h2>{user.name}</h2>
            </div>

            <div className="crew-info-grid">

              <div className="crew-field">
                <label>EMP no</label>
                <p>{user.employee_no}</p>
              </div>

              <div className="crew-field">
                <label>POSITION</label>
                <p>{user.position || "-"}</p>
              </div>

              <div className="crew-field-last">
                <label>Type</label>
                <p>{user.aircraft_type || "-"}</p>
              </div>

            </div>

            <div className="crew-exp-section">
<div className={`expiry-item ${getExpiryClass(medicalRemaining)}`}>
  <span>Medical</span>
  <strong>{formatDate(user.medical_expires_at)}</strong>
  {medicalRemaining !== null && (
    <small>
      {medicalRemaining <= 0
        ? "Expired"
        : `${medicalRemaining} days remaining`}
    </small>
  )}
</div>

<div className={`expiry-item ${getExpiryClass(passportRemaining)}`}>
  <span>Passport</span>
  <strong>{formatDate(user.passport_expires_at)}</strong>
  {passportRemaining !== null && (
    <small>
      {passportRemaining <= 0
        ? "Expired"
        : `${passportRemaining} days remaining`}
    </small>
  )}
</div>

<div className={`expiry-item ${getExpiryClass(licenseRemaining)}`}>
  <span>License</span>
  <strong>{formatDate(user.license_expires_at)}</strong>
  {licenseRemaining !== null && (
    <small>
      {licenseRemaining <= 0
        ? "Expired"
        : `${licenseRemaining} days remaining`}
    </small>
  )}
</div>


             


            </div>
          </div>
        </div>

        <Link to="/dashboard/profile/edit" className="CreateProfileButton">
          <img src={crewProfileSvg} alt="" /> Edit Profile
        </Link>

      </div>
    </PageWrapper>
  );
};

export default Profile;
