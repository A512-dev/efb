// import { useState } from "react";
// import { AuthContext } from "./AuthContext";

// export const AuthProvider = ({ children }) => {
  
//   const [user, setUser] = useState({
//     name: "Test User",
//     role: "admin",
//   });

    
//     // const [user, setUser] = useState(null);

//   return (
//     <AuthContext.Provider value={{ user, setUser }}>
//       {children}
//     </AuthContext.Provider>
//   );
// };

import { useState, useEffect } from "react";
import { AuthContext } from "./AuthContext";
import apiClient from "../services/apiClient";
import { loginUser, logoutUser } from "../services/apiService";

const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const initAuth = async () => {
      const savedUser = localStorage.getItem("user");
      const refreshToken = localStorage.getItem("refresh_token");

      if (!savedUser || !refreshToken) {
        setLoading(false);
        return;
      }

      try {
        
        const response = await apiClient.post("/auth/refresh", {
          refresh_token: refreshToken,
        });

        const newAccess = response.data.access_token;

        localStorage.setItem("access_token", newAccess);
        setUser(JSON.parse(savedUser));
      } catch (err) {
        
        localStorage.clear();
      }

      setLoading(false);
    };

    initAuth();
  }, []);

  const login = async (email, password) => {
    const data = await loginUser(email, password);

    localStorage.setItem("access_token", data.access_token);
    localStorage.setItem("refresh_token", data.refresh_token);
    localStorage.setItem("user", JSON.stringify(data.user));

    setUser(data.user);
  };

  const logout = async () => {
    const refresh = localStorage.getItem("refresh_token");
    if (refresh) {
      await logoutUser(refresh);
    }

    localStorage.clear();
    setUser(null);
    window.location = "/";
  };

  
  if (loading) return <div>Loading...</div>;

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthProvider;
