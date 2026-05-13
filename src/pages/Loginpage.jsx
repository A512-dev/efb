import { useState } from "react";
import { useAuth } from "../auth/useAuth";
import { useNavigate } from "react-router-dom";
import ThemeToggle from "../components/themetoggle";
import loginImg from '../assets/icons/Skytech-logo-transparent (1).png';
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


  return (
  
  <div>
  <div className="loginBox">
    <form  onSubmit={submit}>
      <h2>Login</h2>

      <input type="email" className="loginInput" placeholder="Email"
        onChange={(e) => setEmail(e.target.value)} />

      <input type="password" className="loginInput" placeholder="Password" 
        onChange={(e) => setPassword(e.target.value)} />

      <button className="loginBtn" type="submit">Login</button>
      <div class="loginLinks">
        <a href="#">Forgot password?</a>
        
      </div>  
    
    </form>
    
    <img src={loginImg} alt="" className="imgLogin"/>  
  <ThemeToggle />
    </div>
    
    </div>
  );
}
export default Loginpage