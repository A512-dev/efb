import SideBar from "../components/SideBar";
import { Outlet } from "react-router-dom";

const DashboardLayout= ()=>{

    return(
        <>
        <div  className="SideBar">
            <SideBar />
        </div>
        <div className="contents"> 
            <Outlet />  
        </div>
        </>
    )
}

export default DashboardLayout;