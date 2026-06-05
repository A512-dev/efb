import { NavLink } from "react-router-dom";
import { useManuals } from "../hooks/useManuals";
import { useDownloadManual } from "../hooks/useDownloadManual";
import downloadSvg from '../assets/icons/Import-File--Streamline-Ultimate.svg'
import folderSvg from '../assets/icons/Office-Folder--Streamline-Ultimate.svg'
import backIcon from '../assets/icons/arrowback .svg'
import PageWrapper from "../components/PageWrapper";
const A300_600 =( ) =>{
    const { manuals, loading } = useManuals();
  const { handleDownload } = useDownloadManual();

  if (loading) return <p>Loading manuals...</p>;
return(
    <>
    <PageWrapper>
    <div className="manualsContainerLeft">
      <div className="div-header">
        <NavLink className="card-header1" to={'/dashboard/allDocuments'}> <img src={backIcon} style={{width:'25px'}} alt="" /> </NavLink>
      <NavLink className="card-header2 active" > A300_600 </NavLink>
      
    </div>
      <NavLink className={'headersForManuals'} to="/dashboard/aircraftdocuments">Aircraft documents</NavLink>
      <NavLink className={'headersForManuals'} to="/dashboard/aircraftdocuments"> Aircraft performance</NavLink>
      <NavLink className={'headersForManuals'} to="/dashboard/aircraftdocuments"> Fleet Memos</NavLink>
      <NavLink className={'headersForManuals'} to="/dashboard/aircraftdocuments"> General</NavLink>
      <NavLink className={'headersForManuals'} to="/dashboard/aircraftdocuments"> MEL CDl </NavLink>
      <NavLink className={'headersForManuals'} to="/dashboard/aircraftdocuments"> Training Documents </NavLink>
    </div>
    </PageWrapper>
    </>
)
}
export default A300_600