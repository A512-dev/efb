import { useManuals } from "../hooks/useManuals";
import { useDownloadManual } from "../hooks/useDownloadManual";
import downloadSvg from '../assets/icons/Import-File--Streamline-Ultimate.svg'
import folderSvg from '../assets/icons/Office-Folder--Streamline-Ultimate.svg'
import { NavLink } from "react-router-dom";
const Manuals = () =>{

  const { manuals, loading } = useManuals();
  const { handleDownload } = useDownloadManual();

  if (loading) return <p>Loading manuals...</p>;

  return (
    <>
    <div className="manualsContainerLeft">
      <div className="div-header">
        <NavLink className="card-header1 active" to={'/dashboard/allDocuments'}>All documents </NavLink>
      <NavLink className="card-header2"  to={ '/dashboard/clipboard'}>Clipboard </NavLink>
      
    </div>
      <NavLink className={'headersForManuals'} to="/dashboard/a300_600">A300/600</NavLink>
      {/* a */}
      <NavLink className={'headersForManuals'} to="/dashboard/manuals/chat"> Training & Resources</NavLink>
      <NavLink className={'headersForManuals'} to="/dashboard/forms"> Forms</NavLink>
      <NavLink className={'headersForManuals'} to="/dashboard/manuals/chat"> Safety Issue </NavLink>
      
      {/* <NavLink to="/dashboard/safetyIssue" className={'headersForManuals'}><img src={safetyIssueSvg} alt="" className="navIcon" /> Safety Issue</NavLink>
      <NavLink to="/dashboard/trainingIssue" className={'headersForManuals'}><img src={trainingIssueSvg} alt="" className="navIcon" /> Training Issue</NavLink> */}
      {/* <NavLink to="/dashboard/checkList" className={'headersForManuals'}><img src={checkListSvg} alt="" className="navIcon" /> Check list</NavLink>   */}

      
      {/* <h5 className="headersForManuals" onClick={()=>{ document.querySelector('.manualsContainerLeft').style.height=document.querySelector('.manualsContainerLeft').style.height==='auto' ? '0' : 'auto';}}><img src={folderSvg} alt="" style={{width:"16px ",marginRight:'6%'}}/>training issue</h5> */}
      {/* <h5 className="headersForManuals" onClick={()=>{ document.querySelector('.manualsContainerLeft').style.height=document.querySelector('.manualsContainerLeft').style.height==='auto' ? '0' : 'auto';}}><img src={folderSvg} alt="" style={{width:"16px ",marginRight:'6%'}}/>Operational</h5>
      <h5 className="headersForManuals" onClick={()=>{ document.querySelector('.manualsContainerLeft').style.height=document.querySelector('.manualsContainerLeft').style.height==='auto' ? '0' : 'auto';}}><img src={folderSvg} alt="" style={{width:"16px ",marginRight:'6%'}}/>Flight Manuals</h5>
      <h5 className="headersForManuals" onClick={()=>{ document.querySelector('.manualsContainerLeft').style.height=document.querySelector('.manualsContainerLeft').style.height==='auto' ? '0' : 'auto';}}> <img src={folderSvg} alt="" style={{width:"16px ",marginRight:'6%'}}/>SOPs </h5>
      <h5 className="headersForManuals" onClick={()=>{ document.querySelector('.manualsContainerLeft').style.height=document.querySelector('.manualsContainerLeft').style.height==='auto' ? '0' : 'auto';}}><img src={folderSvg} alt="" style={{width:"16px ",marginRight:'6%'}}/>Training </h5>
      <h5 className="headersForManuals" onClick={()=>{ document.querySelector('.manualsContainerLeft').style.height=document.querySelector('.manualsContainerLeft').style.height==='auto' ? '0' : 'auto';}}> <img src={folderSvg} alt="" style={{width:"16px ",marginRight:'6%'}} />Checklists </h5> */}
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
  );
}
export default Manuals