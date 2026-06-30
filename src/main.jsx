import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './assets/index.css'
import App from './app/App.jsx'
import "react-pdf/dist/Page/TextLayer.css";
import "react-pdf/dist/Page/AnnotationLayer.css";


createRoot(document.getElementById('root')).render(
  <StrictMode>

    <App />

  </StrictMode>,
)
