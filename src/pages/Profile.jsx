import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useCurrentUser } from "../hooks/useCurrentUser";
import {
  downloadMyProfilePicture,
  getMyManualReads,
} from "../services/apiService";
import PageWrapper from "../components/PageWrapper";
import cardImg from "../assets/icons/2d3ae130-4dab-480a-9f81-1612825326e5.webp";
import crewProfileSvg from "../assets/icons/Following-1--Streamline-Ultimate.svg";
import { useManuals } from "../hooks/useManuals";

const Profile = () => {
  const { user, loading } = useCurrentUser();
  const { manuals } = useManuals(null);

  const [profileImage, setProfileImage] = useState(null);
  const [readManuals, setReadManuals] = useState([]);

  const calcRemainingDays = (date) => {
    if (!date) return null;

    const now = new Date();
    const exp = new Date(date);
    const diff = exp - now;

    return Math.ceil(diff / (1000 * 60 * 60 * 24));
  };

  const getExpiryClass = (days) => {
    if (days === null) return "";
    if (days <= 10) return "expire-red";
    if (days <= 30) return "expire-yellow";
    return "expire-green";
  };

  const formatDate = (date) => {
    if (!date) return "-";

    return new Date(date).toLocaleDateString("en-GB", {
      day: "2-digit",
      month: "short",
      year: "numeric",
    });
  };

  const getReadManualId = (item) => {
    return item.manual_id || item.manualId || item.manual?.id;
  };

  const getManualTitle = (item) => {
    const manualId = getReadManualId(item);

    if (item.manual?.title) {
      return item.manual.title;
    }

    const manual = manuals.find(
      (m) => String(m.id) === String(manualId)
    );

    return manual?.title || `Manual #${manualId}`;
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

  useEffect(() => {
    const loadReadManuals = async () => {
      try {
        const data = await getMyManualReads();
        setReadManuals(Array.isArray(data) ? data : data?.items || []);
      } catch (err) {
        console.error("Failed to load read manuals:", err);
      }
    };

    loadReadManuals();
  }, []);

  if (loading) return <div>Loading...</div>;
  if (!user) return <div>Not authenticated</div>;

  const medicalRemaining = calcRemainingDays(user.medical_expires_at);
  const passportRemaining = calcRemainingDays(user.passport_expires_at);
  const licenseRemaining = calcRemainingDays(user.license_expires_at);

  return (
    <PageWrapper>
      <div className="crew-page-wrapper">
        <div className="crew-main-card">
          <div className="crew-left-section">
            <div className="id-card-container" style={{ position: "relative" }}>
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
          <img src={crewProfileSvg} alt="" />
          Edit Profile
        </Link>
      </div>
      <div className="profileManualReads">
  <div className="profileManualHeader">
    <h3>Read Manuals</h3>
    <span className="manualCount">{readManuals.length}</span>
  </div>

  {readManuals.length === 0 ? (
    <p className="noManuals">No manuals read yet</p>
  ) : (
    <div className="readManualList">
      {readManuals.map((item) => {
        const manualId = getReadManualId(item);

        return (
          <div key={item.id || manualId} className="readManualRow">
            <span className="manualTitle">
              {getManualTitle(item)}
            </span>

            {item.read_at && (
              <span className="manualDate">
                {formatDate(item.read_at)}
              </span>
            )}
          </div>
        );
      })}
    </div>
  )}
</div>
    </PageWrapper>
  );
};

export default Profile;
