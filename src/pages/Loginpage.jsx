import { useState } from "react";
import { useAuth } from "../auth/useAuth";
import { useNavigate } from "react-router-dom";

const Loginpage = () =>{
  const { login } = useAuth();
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  
  const submit = async (e) => {
    e.preventDefault();

    try {
      await login(email, password);
      navigate("/dashboard");
    } catch (err) {
      alert("Login failed");
    }
  };
const changeMode = () =>{
  
  document.querySelector('body').style.backgroundColor=document.querySelector('body').style.backgroundColor== '#f7f8fa' ? 'rgb(30, 32, 36)' :'#f7f8fa'

}

  return (
  
  
  
    <form onSubmit={submit}>
      <h2>Login</h2>

      <input type="email" className="loginInput" placeholder="Email"
        onChange={(e) => setEmail(e.target.value)} />

      <input type="password" className="loginInput" placeholder="Password" 
        onChange={(e) => setPassword(e.target.value)} />

      <button type="submit">Login</button>
      
    </form>
  
    
  );
}
export default Loginpage