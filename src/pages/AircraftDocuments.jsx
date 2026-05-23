import { NavLink } from "react-router-dom";
import { useManuals } from "../hooks/useManuals";
import { useDownloadManual } from "../hooks/useDownloadManual";
import downloadSvg from '../assets/icons/Import-File--Streamline-Ultimate.svg'
import folderSvg from '../assets/icons/Office-Folder--Streamline-Ultimate.svg'
import sopfile from '../assets/files/A306-310-SOP.pdf'
const AircraftDocuments = ()=>{
    const { manuals, loading } = useManuals();
  const { handleDownload } = useDownloadManual();

  if (loading) return <p>Loading manuals...</p>;
console.log(manuals[0])
return (
    <>
    <div className="manualsContainerLeft">
      <div className="div-header">
        <NavLink className="card-header1" to={'/dashboard/allDocuments'}>all documents </NavLink>
      <NavLink className="card-header2" to={ '/dashboard/clipboard'} >Clipboard </NavLink>
      
    </div>
      <NavLink className={'headersForManuals'} to="/dashboard/aircraftdocuments">Aircraft documents</NavLink>
      <NavLink className={'headersForManuals'} to="/dashboard/manuals/chat"> Aircraft performance</NavLink>
      <NavLink className={'headersForManuals'} to="/dashboard/manuals/chat"> fleet memos</NavLink>
      <NavLink className={'headersForManuals'} to="/dashboard/manuals/chat"> general</NavLink>
      <NavLink className={'headersForManuals'} to="/dashboard/manuals/chat"> MEL CDl </NavLink>
      <NavLink className={'headersForManuals'} to="/dashboard/manuals/chat"> Training documents </NavLink>
    </div>
    <div className="manualsContainer">

  <h2 className="card-header">Manuals</h2>

<h3>{manuals[0].title}</h3>
<p>{manuals[0].original_filename}</p>
<button
        onClick={() => handleDownload(manuals[0])}
        className="downloadBtn"
      >
        <img src={downloadSvg} style={{width:"16px"}}/>
        Download
      </button>
  
</div>
    </>
)
}

export default AircraftDocuments;