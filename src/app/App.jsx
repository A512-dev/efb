import { useState } from 'react'
import '../assets/App.css'
import AppRouter from '../router/AppRouter'
import AuthProvider  from "../auth/AuthProvider";
import ThemeToggle from '../components/themetoggle';
import "../assets/theme.css";

const App= ()=> {
  

  return (
    <>
    <AuthProvider>

        <ThemeToggle />
              <AppRouter />
        

    </AuthProvider>
    </>
  )
}

export default App
