import { NavLink } from "react-router-dom";
import { useManuals } from "../hooks/useManuals";
import { useDownloadManual } from "../hooks/useDownloadManual";
import downloadSvg from '../assets/icons/Import-File--Streamline-Ultimate.svg'
import folderSvg from '../assets/icons/Office-Folder--Streamline-Ultimate.svg'
const AllDocuments =( ) =>{
    const { manuals, loading } = useManuals();
  const { handleDownload } = useDownloadManual();

  if (loading) return <p>Loading manuals...</p>;
return(
    <>
    <div className="manualsContainerLeft">
      <div className="div-header">
        <NavLink className="card-header1" to={'/dashboard/allDocuments'}>All Documents </NavLink>
      <NavLink className="card-header2" to={ '/dashboard/clipboard'} >Clipboard </NavLink>
      
    </div>
      <NavLink className={'headersForManuals'} to="/dashboard/A300_600">A300/600</NavLink>
      {/* <NavLink to="/dashboard/A300_600" className={'headersForManuals'}>Iranair</NavLink> */}
      <NavLink className={'headersForManuals'} to="/dashboard/A300_600"> Training & Resources</NavLink>
      <NavLink className={'headersForManuals'} to="/dashboard/forms"> Forms</NavLink>
      <NavLink className={'headersForManuals'} to="/dashboard/A300_600"> Safety Issue </NavLink>
    </div>
    {/* <div className="manualsContainer">

  <h2 className="card-header">Manuals</h2>


  {manuals.map((manual) => (
    <div key={manual.id} className="manualItem">

      <div className="manualLeft">
        

        <div>
          <h3>{manual.title}</h3>
          <p>{manual.original_filename}</p>
        </div>
      </div>

      <button
        onClick={() => handleDownload(manual)}
        className="downloadBtn"
      >
        <img src={downloadSvg} style={{width:"16px"}}/>
        Download
      </button>

    </div>
  ))}

</div> */}
    </>
)
}
export default AllDocuments