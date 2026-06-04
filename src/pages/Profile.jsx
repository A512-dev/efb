// import { useCurrentUser } from "../hooks/useCurrentUser";
// import logoutSvg from '../assets/icons/Power-Button--Streamline-Ultimate.svg'
// import { useAuth } from "../auth/useAuth";
// import ccccccc from '../assets/icons/2d3ae130-4dab-480a-9f81-1612825326e5.webp'
// const Profile =( ) =>{
//     const {user,loading}=useCurrentUser()
//     const { logout } = useAuth();
//      if (loading) return <div>Loading...</div>;

//   if (!user) return
  
//   if (!user) return  <div>Not authenticated</div>;
// return (
//     <>
    
//     <div className="div-main">
//         <img src={ccccccc} alt="" className="imgProfile "/>
//     <div className="divProfileItems">
//         <h3 className="ProfileItems"> Name: {user.name}</h3>
    
//      <h3 className="ProfileItems"> EMP no: {user.id}</h3>
//      <h3 className="ProfileItems">Position: P2 </h3>
//      <h3 className="ProfileItems">Type: 310 </h3>
//           <h3 className="ProfileItems">Medical expire:{} <span className="RemainItems"> Remain: </span> </h3>
//                <h3 className="ProfileItems">Passport expire:{} <span className="RemainItems"> Remain: </span> </h3>
//     <h3 className="ProfileItems">LPR expire: {} <span className="RemainItems">   Remain: </span></h3>
//     </div>


//     </div>
    
//     <button onClick={logout} className="logOutButton"><img src={logoutSvg} alt="" /> Logout</button>
//     </>
// )
// }

// export default Profile
import { useCurrentUser } from "../hooks/useCurrentUser";
import cardImg from "../assets/icons/2d3ae130-4dab-480a-9f81-1612825326e5.webp";
import logoutSvg from '../assets/icons/Power-Button--Streamline-Ultimate.svg'
import { useAuth } from "../auth/useAuth";
import crewProfileSvg from "../assets/icons/Following-1--Streamline-Ultimate.svg";
const Profile = () => {
  const { user, loading } = useCurrentUser();  


    const { logout } = useAuth();
     if (loading) return <div>Loading...</div>;

  


  if (!user) return
  
  if (!user) return  <div>Not authenticated</div>;
  return (
    <div className="crew-page-wrapper">
      <div className="crew-main-card">

        
        <div className="crew-left-section">
          <div className="flip-card">
            <div className="flip-card-inner">

              
              <div className="flip-card-front">
                <img
                  src={cardImg}
                  className="crew-card-img"
                  alt="Crew ID Card"
                />
              </div>


              <div className="flip-card-back">
                <div className="back-content">
                  <h3>Quick Stats</h3>

                  <div className="back-stat">
                    <span>Flights This Month</span>
                    <strong>12</strong>
                  </div>

                  <div className="back-stat">
                    <span>Total Hours</span>
                    <strong>4,250</strong>
                  </div>

                  <div className="back-stat">
                    <span>Status</span>
                    <strong className="status-active">
                      Active Duty
                    </strong>
                  </div>
                </div>
              </div>

            </div>
          </div>
        </div>


        <div className="crew-right-section">

          <div className="crew-header">
            <h2>{user.name}</h2>
            <span className="crew-role">
              First Officer • A310 Fleet
            </span>
          </div>

          <div className="crew-info-grid">

            <div className="crew-field">
              <label>EMPLOYEE ID</label>
              <p>{user.id}</p>
            </div>

            <div className="crew-field">
              <label>BASE</label>
              <p>IKA</p>
            </div>

            <div className="crew-field">
              <label>POSITION</label>
              <p>P2</p>
            </div>

            <div className="crew-field">
              <label>AIRCRAFT</label>
              <p>Airbus A310</p>
            </div>

          </div>

          <div className="crew-exp-section">

            <div className="expiry-item">
              <span>Medical</span>
              <strong>20 Dec 2024</strong>
              <small>120 days remaining</small>
            </div>

            <div className="expiry-item warn">
              <span>Passport</span>
              <strong>15 Jul 2024</strong>
              <small>12 days remaining</small>
            </div>

            <div className="expiry-item">
              <span>License</span>
              <strong>03 Jan 2025</strong>
              <small>210 days remaining</small>
            </div>

          </div>

        </div>

      </div>
           <button onClick={logout} className="logOutButton"><img src={logoutSvg} alt="" /> Logout</button>
           <button className="CreateProfileButton"><img src={crewProfileSvg} alt="" /> Create / edit profile</button>
    </div>
  );
};

export default Profile;
