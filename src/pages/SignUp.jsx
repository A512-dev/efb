import { createPilotUser } from "../services/apiService";
const SignUp = () =>{
 const handleCreatePilot = async () => {
    try {
      const newUser = await createPilotUser();
alert("Pilot created: " + newUser.email);
    } catch (err) {
      console.error(err);
      alert("ساخت کاربر جدید با خطا مواجه شد");
    }
  };
return (
    <>
    <label htmlFor="pilotName">name of the pilot</label>
    <input type="text" name="pilotName" placeholder="insert pilots name" />

    <button onClick={handleCreatePilot}>createOne</button>
    </>
)
}

export default SignUp;