import { useState } from "react";
import PageWrapper from "../components/PageWrapper";
import { NavLink } from "react-router-dom";
import backIcon from '../assets/icons/arrowback .svg';

const InsideFolder = () => {
    
    const files = [
        { name: "_tmp_FLT26060218_ IRAN(1)", filename: "_tmp_FLT26060218_IRAN(1).pdf" },
        { name: "_tmp_SIGWX_ IRAN18.jpg", filename: "_tmp_SIGWX_IRAN18.jpg" },
        { name: "_tmp_SIGWX_ WEST18.jpg", filename: "_tmp_SIGWX_WEST18.jpg" },
        { name: "DISPATCH  RELEASE FORM.pdf", filename: "DISPATCH  RELEASE FORM.pdf" },
        { name: "IRA1553_ 2Jun2026_EPIBK_ OEJN2010_OIMM2355 _2026FBFGDTA.pdf", filename: "IRA1553_2Jun2026_EPIBK_OEJN2010_OIMM2355_2026FBFGDTA.pdf" },
        { name: "MELCDL.pdf", filename: "MELCDL.pdf" },
    ];

    
    const [selectedFile, setSelectedFile] = useState(files[0].filename);

    return (
        <PageWrapper>
            <div className="manualsContainerLeft">
                <div className="div-header">
                    <NavLink 
                        className="card-header1" 
                        style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}
                        to={"/dashboard/FlightFolder"}
                    >
                        <img src={backIcon} alt="back" style={{ width: "23px" }} />
                    </NavLink>
                    
                    <div className="card-header2" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                        PLAN 1552 IBK
                    </div>
                </div>

                
                <div className="file-list" style={{ padding: "10px" }}>
                    {files.map((file, index) => (
                        <div  className="headersForManuals"
                            key={index}
                            onClick={() => setSelectedFile(file.filename)}
                        >
                            {file.name}
                        </div>
                    ))}
                </div>
            </div>

            <div className="manualsContainer" style={{ height: '88vh' }}>
                
                <iframe
                    src={`/${selectedFile}`}
                    width="100%"
                    height="100%"
                    style={{ border: "none" }}
                    title="Document preview"
                />
            </div>
        </PageWrapper>
    );
};

export default InsideFolder;
