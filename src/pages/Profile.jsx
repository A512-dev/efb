import { useCurrentUser } from "../hooks/useCurrentUser";
import logoutSvg from '../assets/icons/Power-Button--Streamline-Ultimate.svg'
import { useAuth } from "../auth/useAuth";
import pilotProfile from '../assets/icons/7e4a0f8a-a628-4727-8735-43fe3ceffb19.webp'
const Profile =( ) =>{
    const {user,loading}=useCurrentUser()
     if (loading) return <div>Loading...</div>;

  if (!user) return
  console.log(user)
  const { logout } = useAuth();

  if (!user) return  <div>Not authenticated</div>;
return (
    <>
    <div className="div-main">
        <img src={pilotProfile} alt="" className="imgProfile "/>
    <h3 className="ProfileItems"> Name: {user.name}</h3>
    
     <h3 className="ProfileItems"> EMP no: {user.id}</h3>
     <h3 className="ProfileItems">Position: P2 </h3>
     <h3 className="ProfileItems">Type: 310 </h3>
          <h3 className="ProfileItems">Medical expire:{} <span className="RemainItems"> Remain: </span> </h3>
               <h3 className="ProfileItems">Passport expire:{} <span className="RemainItems"> Remain: </span> </h3>
    <h3 className="ProfileItems">LPR expire: {} <span className="RemainItems">   Remain: </span></h3>


    </div>
    <button onClick={logout} className="logOutButton"><img src={logoutSvg} alt="" /> Logout</button>
    </>
)
}

export default Profile