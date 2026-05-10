import { useManuals } from "../hooks/useManuals";
import { useDownloadManual } from "../hooks/useDownloadManual";

const Manuals = () =>{

  const { manuals, loading } = useManuals();
  const { handleDownload } = useDownloadManual();

  if (loading) return <p>Loading manuals...</p>;

  return (
    <div>

      <h2>Manuals</h2>

      {manuals.map((manual) => (

        <div key={manual.id} style={{marginBottom: "20px"}}>

          <h3>{manual.title}</h3>

          <p>{manual.original_filename}</p>

          <button onClick={() => handleDownload(manual)}>
            Download
          </button>

        </div>

      ))}

    </div>
  );
}
export default Manuals