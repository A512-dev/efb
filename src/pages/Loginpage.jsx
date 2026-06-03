// import { useState } from "react";
// import { useAuth } from "../auth/useAuth";
// import { useNavigate } from "react-router-dom";
// import ThemeToggle from "../components/ThemeToggle";
// import loginLogo from '../assets/icons/Skytech-logo-transparent (1).png';
// import loginImg from "../assets/icons/bgEFB..webp"
// const Loginpage = () =>{
//   const { login } = useAuth();
//   const navigate = useNavigate();

//   const [email, setEmail] = useState("");
//   const [password, setPassword] = useState("");
  
//   const submit = async (e) => {
//     e.preventDefault();

//     try {
//       await login(email, password);
//       navigate("/dashboard");
//     } catch (err) {
//       alert("Login failed");
//     }
//   };


//   return (
  
//   <div>
//   <div className="loginBox">
//     <form  className="LoginRedesigned" onSubmit={submit}>
//       <h2>Login</h2>

//       <input type="email" className="loginInput" placeholder="Email"
//         onChange={(e) => setEmail(e.target.value)} />

//       <input type="password" className="loginInput" placeholder="Password" 
//         onChange={(e) => setPassword(e.target.value)} />

//       <button className="loginBtn" type="submit">Login</button>
//       <div class="loginLinks">
//         <a style={{color:'#000000'}} href="#">Forgot password?</a>
        
//       </div>  
//     <img src={loginImg} alt="" className="imgLogin"/>  
//     </form>
    
    
//   <ThemeToggle />
//     </div>
    
//     </div>
//   );
// }
// export default Loginpage

import { useState } from "react";
import { useAuth } from "../auth/useAuth"; 
import { useNavigate } from "react-router-dom"; 
import ThemeToggle from "../components/ThemeToggle";
import loginLogo from '../assets/icons/Skytech-logo-transparent (1).png';
<<<<<<< HEAD
import loginImg from "../assets/icons/bgEFB..webp";
=======
import loginImg from "../assets/icons/9b1a7dde-b3c2-402f-9543-b3b2e7261a19.png";
>>>>>>> origin/main

const Loginpage = () => {
  const { login } = useAuth(); 
  const navigate = useNavigate();

  
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  
  const [error, setError] = useState("");
  
  const [isLoading, setIsLoading] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setError(""); 
    setIsLoading(true);

    try {
      
      await login(email, password);
      
      setError("");
      navigate("/dashboard");
    } catch (err) {
      
      if (err.response && err.response.status === 401) {
        setError("Invalid email or password.");
      } else {
        setError("Login failed. Please try again.");
      }
    } finally {
      setIsLoading(false); 
    }
  };

  return (
    <div>
      <div className="loginBox">
        <form className="LoginRedesigned" onSubmit={submit}>
          <h2>Login</h2>

          
          
          <input
            id="emailInput"
            type="email"
            className="loginInput"
            placeholder="Email"
            value={email}
            onChange={(e) => {
              setEmail(e.target.value);
              setError("");
            }}
            disabled={isLoading} 
            required
          />

          
          
          <input
            id="passwordInput"
            type="password"
            className="loginInput"
            placeholder="Password"
            value={password}
            onChange={(e) => {
              setPassword(e.target.value);
              setError(""); 
            }}
            disabled={isLoading}
            required
          />

          
          {error && <p className="loginError">{error}</p>}

          
          <button className="loginBtn" type="submit" disabled={isLoading}>
            {isLoading ? "Logging in..." : "Login"}
          </button>

          <div className="loginLinks">
            
            <a href="#" style={{ color: '#000000' }}>Forgot password?</a>
        
        
          </div>

        
          <img src={loginImg} alt="Login illustration" className="imgLogin" />
        </form>

        
        
      </div>
    </div>
  );
}

export default Loginpage;
