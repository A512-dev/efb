import { useManuals } from "../hooks/useManuals";
import { useDownloadManual } from "../hooks/useDownloadManual";
import downloadSvg from '../assets/icons/Import-File--Streamline-Ultimate.svg'
import folderSvg from '../assets/icons/Office-Folder--Streamline-Ultimate.svg'
const Manuals = () =>{

  const { manuals, loading } = useManuals();
  const { handleDownload } = useDownloadManual();

  if (loading) return <p>Loading manuals...</p>;

  return (
    <>
    <div className="manualsContainerLeft">
      <h2 className="card-header">Classification </h2>
      <h5 className="headersForManuals"><img src={folderSvg} alt="" style={{width:"16px ",marginRight:'6%'}}/>Operational</h5>
      <h5 className="headersForManuals"><img src={folderSvg} alt="" style={{width:"16px ",marginRight:'6%'}}/>Flight Manuals</h5>
      <h5 className="headersForManuals"><img src={folderSvg} alt="" style={{width:"16px ",marginRight:'6%'}}/>SOPs </h5>
      <h5 className="headersForManuals"><img src={folderSvg} alt="" style={{width:"16px ",marginRight:'6%'}}/>Training </h5>
      <h5 className="headersForManuals"> <img src={folderSvg} alt="" style={{width:"16px ",marginRight:'6%'}} />Checklists </h5>
    </div>
    <div className="manualsContainer">

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

</div>
</>
  );
}
export default Manuals