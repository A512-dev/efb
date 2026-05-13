import { useCurrentUser } from "../hooks/useCurrentUser";

const Profile =( ) =>{
    const {user,loading}=useCurrentUser()
     if (loading) return <div>Loading...</div>;

  if (!user) return <div>Not authenticated</div>;
  console.log(user)
return (
    <>
    <div className="div-main">
    <h3>{user.name}</h3>
     <h3> badge number: {user.id}</h3>
    </div>
    </>
)
}

export default Profile