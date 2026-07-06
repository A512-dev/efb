import { useState } from "react";
import { useNavigate } from "react-router-dom"; 
import { Eye, EyeOff } from "lucide-react";
import { changePassword } from "../services/apiService";

import loginImg from "../assets/icons/bgEFB..webp";

const ChangePassword = () => {
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [signupKey, setSignupKey] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [isLoading, setIsLoading] = useState(false);


  const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&#])[A-Za-z\d@$!%*?&#]{8,}$/;

  const validateInputs = () => {
    if (!email || !signupKey || !newPassword || !confirmPassword) {
      setError("All fields are required.");
      return false;
    }
    

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      setError("Please enter a valid email address.");
      return false;
    }

    if (!passwordRegex.test(newPassword)) {
      setError("Password must be at least 8 characters long and include uppercase, lowercase, number, and a special symbol.");
      return false;
    }

    if (newPassword !== confirmPassword) {
      setError("New password and confirm password do not match.");
      return false;
    }

    return true;
  };

  const submit = async (e) => {
    e.preventDefault();
    setError(""); 
    setSuccess("");

    if (!validateInputs()) return;

    setIsLoading(true);

    try {
      await changePassword(email, signupKey, newPassword);
      setSuccess("Password changed successfully! Redirecting to login...");
      
      setTimeout(() => {
        navigate("/");
      }, 2000);
    } catch (err) {
      const apiError = err.response?.data?.error || "Failed to change password. Please check your credentials.";
      setError(apiError);
    } finally {
      setIsLoading(false); 
    }
  };

  return (
    <div className="change-password-container">
      <div className="loginBox">
        <form className="LoginRedesigned" onSubmit={submit} noValidate>
          <h2>Set Initial Password</h2>


          <div className="input-group">
            <input
              id="emailInput"
              type="email"
              className={`loginInput ${error && !email ? "input-error" : ""}`}
              placeholder="Email Address"
              value={email}
              onChange={(e) => { setEmail(e.target.value); setError(""); }}
              disabled={isLoading} 
            />
          </div>

          <div className="input-group">
            <input
              id="signupKeyInput"
              type="text"
              className={`loginInput ${error && !signupKey ? "input-error" : ""}`}
              placeholder="Signup Key"
              value={signupKey}
              onChange={(e) => { setSignupKey(e.target.value); setError(""); }}
              disabled={isLoading} 
            />
          </div>

          <div className="input-group password-group">
            <input
              id="passwordInput"
              type={showPassword ? "text" : "password"}
              placeholder="New Password"
              value={newPassword}
              onChange={(e) => { setNewPassword(e.target.value); setError(""); }}
              disabled={isLoading}
              className={`loginInput ${error && !newPassword ? "input-error" : ""}`}
            />
            <button
              type="button"
              className="toggle-password"
              onClick={() => setShowPassword((prev) => !prev)}
              aria-label="Toggle password visibility"
            >
              {showPassword ? <EyeOff size={18} color="#666"/> : <Eye size={18} color="#666"/>}
            </button>
          </div>

          <div className="input-group password-group">
            <input
              id="confirmPasswordInput"
              type={showConfirmPassword ? "text" : "password"}
              placeholder="Confirm New Password"
              value={confirmPassword}
              onChange={(e) => { setConfirmPassword(e.target.value); setError(""); }}
              disabled={isLoading}
              className={`loginInput ${error && !confirmPassword ? "input-error" : ""}`}
            />
            <button
              type="button"
              className="toggle-password"
              onClick={() => setShowConfirmPassword((prev) => !prev)}
              aria-label="Toggle confirm password visibility"
            >
              {showConfirmPassword ? <EyeOff size={18} color="#666"/> : <Eye size={18} color="#666"/>}
            </button>
          </div>
          
          <div className="message-container">
            {error && <p className="loginError fade-in">{error}</p>}
            {success && <p className="loginSuccess fade-in">{success}</p>}
          </div>

          <button className="loginBtn" type="submit" disabled={isLoading}>
            {isLoading ? <span className="spinner"></span> : "Change Password"}
          </button>

          <div className="loginLinks">
            <a href="/" onClick={(e) => { e.preventDefault(); navigate("/"); }} className="back-link">
              ← Back to Login
            </a>
          </div>

          <img src={loginImg} alt="Security illustration" className="imgLogin" />
        </form>
      </div>
      <span className='footer-note'>تمامی حقوق مادی و معنوی سایت متعلق به واحد فنا‌ورانه اسکای تک‌ شریف مستقر در پارک علم و فناوری دانشگاه شریف است ©</span>
    </div>
  );
}

export default ChangePassword;
