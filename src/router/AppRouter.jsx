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
import AllDocuments from "../pages/allDocuments";
import Clipboard from "../pages/Clipboard";
import AircraftDocuments from "../pages/AircraftDocuments";
import A300_600 from "../pages/A300_600";
import IranAirChat from "../pages/IranAirChat";
import Setting from "../pages/Setting";
import UpdateManuals from "../pages/UpdateManuals";
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
              path="safetyIssue"
              element={<RequireAuth allowedRoles={["pilot", "viewer", "admin"]} />}
            >
              <Route index element={<Profile />} />
            </Route>
            <Route
              path="trainingIssue"
              element={<RequireAuth allowedRoles={["pilot", "viewer", "admin"]} />}
            >
              <Route index element={<Profile />} />
            </Route>
            <Route
              path="checkList"
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
            <Route path="allDocuments" element={<RequireAuth allowedRoles={["pilot", "viewer", "admin"]} />}
            >
            <Route index element={<AllDocuments/>} />
            </Route>
            <Route path="clipboard" element={<RequireAuth allowedRoles={["pilot", "viewer", "admin"]} />}
            >
            <Route index element={<Clipboard/>} />
            </Route>
            <Route path="A300_600" element={<RequireAuth allowedRoles={["pilot", "viewer", "admin"]} />}
            >
            <Route index element={<A300_600/>} />
            </Route>
            <Route path="aircraftdocuments" element={<RequireAuth allowedRoles={["pilot", "viewer", "admin"]} />}
            >
            <Route index element={<AircraftDocuments/>} />
            </Route>
            <Route path="IranAirChat" element={<RequireAuth allowedRoles={["pilot", "viewer", "admin"]} />}
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
  );
}
