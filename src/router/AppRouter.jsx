import { BrowserRouter, Routes, Route } from "react-router-dom";
import Loginpage from "../pages/Loginpage";
import DashboardLayout from "../layouts/DashboardLayout";
import Dashboard from "../pages/Dashboard";
import Manuals from "../pages/Manuals";
import ManualsAdmin from "../pages/ManualsAdmin";
import Forms from "../pages/Forms";
import RequireAuth from "../auth/RequireAuth";
import Profile from "../pages/Profile";
import SignUp from "../pages/SignUp";

export default function AppRouter() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Loginpage />} />

        <Route element={<RequireAuth />}>
          <Route path="/dashboard" element={<DashboardLayout />}>
            


            <Route
              path="profile"
              element={<RequireAuth allowedRoles={["pilot", "viewer", "admin"]} />}
            >
              <Route index element={<Profile />} />
            </Route>
            <Route
              path="forms"
              element={<RequireAuth allowedRoles={["pilot", "admin"]} />}
            >
              <Route index element={<Forms />} />
            </Route>

            <Route
              path="manuals"
              element={<RequireAuth allowedRoles={["pilot", "viewer", "admin"]} />}
            >
              <Route index element={<Manuals />} />
            </Route>

            <Route
              path="manuals-admin"
              element={<RequireAuth allowedRoles={["admin"]} />}
            >
              <Route index element={<ManualsAdmin />} />
              
            </Route>
            <Route
              path="add-profile"
              element={<RequireAuth allowedRoles={["admin"]} />}
            >
              <Route index element={<SignUp />} />
            </Route>

          </Route>
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
