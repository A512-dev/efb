import { BrowserRouter, Routes, Route } from "react-router-dom";
import Loginpage from "../pages/Loginpage";
import DashboardLayout from "../layouts/DashboardLayout";

import Manuals from "../pages/Manuals";
import ManualsAdmin from "../pages/ManualsAdmin";

import RequireAuth from "../auth/RequireAuth";
import Profile from "../pages/Profile";
import SignUp from "../pages/SignUp";

import Clipboard from "../pages/Clipboard";


import IranAirChat from "../pages/IranAirChat";
import Setting from "../pages/Setting";
import UpdateManuals from "../pages/UpdateManuals";
import { AnimatePresence } from "framer-motion";
export default function AppRouter() {
  return (
      <AnimatePresence mode="wait">
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
              path="manuals"
              element={<RequireAuth allowedRoles={["pilot", "viewer", "admin"]} />}
            >
              <Route index element={<Manuals />} />
              
            </Route>
            <Route
  path="category/:categoryId"
  element={<RequireAuth allowedRoles={["pilot", "viewer", "admin"]} />}
>
  <Route index element={<Manuals />} />
</Route>
            
            <Route
              path="setting"
              element={<RequireAuth allowedRoles={["pilot", "viewer", "admin"]} />}
            >
              <Route index element={<Setting />} />
              
            </Route>
            <Route
              path="UpdateManuals"
              element={<RequireAuth allowedRoles={["pilot", "viewer", "admin"]} />}
            >
              <Route index element={<UpdateManuals />} />
              
            </Route>
            
            <Route path="clipboard" element={<RequireAuth allowedRoles={["pilot", "viewer", "admin"]} />}
            >
            <Route index element={<Clipboard/>} />
            </Route>
            
            
            <Route path="Chat" element={<RequireAuth allowedRoles={["pilot", "viewer", "admin"]} />}
            >
            <Route index element={<IranAirChat/>} />
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
    </AnimatePresence>
  );
}
