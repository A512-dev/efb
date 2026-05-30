import { NavLink } from "react-router-dom"
import ThemeToggle from "../components/ThemeToggle"
const UpdateManuals =()=>
{
return(
    <>
    <div className="manualsContainerLeft">
      <div className="div-header">
        <NavLink className='card-header' to={'/dashboard/setting'} >Settings </NavLink>
      
      
    </div>
      <NavLink className={'headersForManuals'} to="/dashboard/UpdateManuals">Updates</NavLink>
      <NavLink to="/dashboard/manuals" className={'headersForManuals'}>Help</NavLink>
      <NavLink className={'headersForManuals'} to="/dashboard/manuals/chat">What's new</NavLink>
      <h5 className="card-header">App theme</h5>
      
      <div className="divDarkLight"><ThemeToggle />
      
      </div>
      

      
    </div>
    <div className="manualsContainer">
        <div style={{ width: '100%', height: '82vh' }}>
          
        </div>
      </div>
    </>
)
}
export default UpdateManuals