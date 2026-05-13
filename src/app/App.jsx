import '../assets/theme.css'
import AppRouter from '../router/AppRouter'
import AuthProvider  from "../auth/AuthProvider";

import "../assets/theme.css";

const App= ()=> {
  

  return (
    <>
    <AuthProvider>

        
              <AppRouter />
        

    </AuthProvider>
    </>
  )
}

export default App
