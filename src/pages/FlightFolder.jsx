import { useState } from "react"
import PageWrapper from "../components/PageWrapper"
import { NavLink } from "react-router-dom"
const FlightFolder = () =>{
   const [openDoc,setOpenDoc]=useState(false)
return(
    <PageWrapper>
      <div className="manualsContainerLeft">
            <div className="div-header single-header">
            <NavLink className="card-header single" to="#">
              Flight Folders
            </NavLink>
          </div>
<NavLink className="headersForManuals" to="/dashboard/insidefolder">
        PLAN 1552 IBK
            </NavLink>
      
</div>
       
        <div className="manualsContainer">
          <div style={{ width: "100%", height: "100vh" }}>
            
              <iframe
                src={openDoc}
                width="100%"
                height="100%"
                style={{ border: "none" }}s
                title="PDF preview"
              />
            
              <p style={{ padding: "20px" }}>Select a document to preview</p>
            
          </div>
        </div>
      
    </PageWrapper>
)
}

export default FlightFolder