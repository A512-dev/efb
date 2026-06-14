import { useState, useEffect } from "react";
import { AuthContext } from "./AuthContext";
import apiClient from "../services/apiClient";
import { loginUser, logoutUser, getCurrentUser } from "../services/apiService";

const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const refreshUser = async () => {
    try {
      const userData = await getCurrentUser();
      setUser(userData);
      return userData;
    } catch (err) {
      setUser(null);
      throw err;
    }
  };

  useEffect(() => {
    const initAuth = async () => {
      const refreshToken = localStorage.getItem("refresh_token");

      if (!refreshToken) {
        setLoading(false);
        return;
      }

      try {
        const response = await apiClient.post("/auth/refresh", {
          refresh_token: refreshToken,
        });

        const newAccess = response.data.access_token;
        localStorage.setItem("access_token", newAccess);

        await refreshUser();
      } catch (err) {
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        setUser(null);
      } finally {
        setLoading(false);
      }
    };

    initAuth();
  }, []);

  const login = async (email, password) => {
    const data = await loginUser(email, password);

    localStorage.setItem("access_token", data.access_token);
    localStorage.setItem("refresh_token", data.refresh_token);

    await refreshUser();
  };

  const logout = async () => {
    try {
      const refresh = localStorage.getItem("refresh_token");
      if (refresh) {
        await logoutUser(refresh);
      }
    } catch (err) {
      console.log("Logout cleanup");
    } finally {
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
      setUser(null);
      window.location = "/";
    }
  };

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        login,
        logout,
        refreshUser,
        setUser,
        loading,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export default AuthProvider;
