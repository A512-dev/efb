import { useState, useEffect } from "react";
import '../assets/theme.css';
import lightSvg from '../assets/icons/Brightness--Streamline-Ultimate.svg'
import darkSvg from '../assets/icons/Brightness--Streamline-Ultimate copy.svg'
const ThemeToggle = () => {
  const [theme, setTheme] = useState("light");

  useEffect(() => {
    const saved = localStorage.getItem("theme") || "light";
    setTheme(saved);
    document.documentElement.setAttribute("data-theme", saved);
  }, []);


  const toggleTheme = () => {
    const next = theme === "light" ? "dark" : "light";
    setTheme(next);
    document.documentElement.setAttribute("data-theme", next);
    localStorage.setItem("theme", next);
  };

  return (
    <button className="changethemebutton" onClick={toggleTheme}>
      <img
        src={theme === "light" ? darkSvg : lightSvg}
        alt={theme === "light" ? "Dark Mode" : "Light Mode"}
        style={{ width: "20%" , height:'20px' }}className=" lightDarkIcon"
      />
      {theme === "light" ? " Dark Mode" : "Light Mode"}
    </button>
  );
}
export default ThemeToggle