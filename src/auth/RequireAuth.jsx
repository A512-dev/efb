import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "./useAuth";

const RequireAuth = ({ allowedRoles }) => {
  const { user } = useAuth();

  if (!user) return <Navigate to="/" replace />;

  if (allowedRoles && !allowedRoles.includes(user.role)) {
    return <Navigate to="/dashboard" replace />;
  }

  return <Outlet />;
};

export default RequireAuth;
