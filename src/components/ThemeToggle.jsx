// import { useState, useEffect } from "react";
// import '../assets/theme.css';
// import lightSvg from '../assets/icons/Brightness--Streamline-Ultimate.svg'
// import darkSvg from '../assets/icons/Brightness--Streamline-Ultimate copy.svg'
// const ThemeToggle = () => {
//   const [theme, setTheme] = useState("light");

//   useEffect(() => {
//     const saved = localStorage.getItem("theme") || "light";
//     setTheme(saved);
//     document.documentElement.setAttribute("data-theme", saved);
//   }, []);


//   const toggleTheme = () => {
//     const next = theme === "light" ? "dark" : "light";
//     setTheme(next);
//     document.documentElement.setAttribute("data-theme", next);
//     localStorage.setItem("theme", next);
//   };

//   return (
//     <button className="changethemebutton" onClick={toggleTheme}>
//       <img
//         src={theme === "light" ? darkSvg : lightSvg}
//         alt={theme === "light" ? "Dark" : "Light"}
//         style={{ width: "20%" , height:'20px' }}className=" lightDarkIcon"
//       />
//       {theme === "light" ? " Dark" : "Light"}
//     </button>
//   );
// }
// export default ThemeToggle

import { useState, useEffect } from "react";
import "../assets/theme.css";
import lightSvg from "../assets/icons/Brightness--Streamline-Ultimate.svg";
import darkSvg from "../assets/icons/Brightness--Streamline-Ultimate copy.svg";

const ThemeToggle = () => {
  const [theme, setTheme] = useState("light");

  useEffect(() => {
    const saved = localStorage.getItem("theme") || "light";
    setTheme(saved);
    document.documentElement.setAttribute("data-theme", saved);
  }, []);

  const setThemeMode = (mode) => {
    setTheme(mode);
    document.documentElement.setAttribute("data-theme", mode);
    localStorage.setItem("theme", mode);
  };

  return (
    <div className="theme-switch">
      <button
        type="button"
        onClick={() => setThemeMode("light")}
        className={`changethemebutton ${theme === "light" ? "active" : ""} lightbutton`}
      >
        <img
          src={lightSvg}
          alt="Light"
          style={{ width: "20px", height: "20px" }}
          className="lightDarkIcon"
        />
        Light
      </button>

      <button
        type="button"
        onClick={() => setThemeMode("dark")}
        className={`changethemebutton ${theme === "dark" ? "active" : ""} darkbutton`}
      >
        <img
          src={darkSvg}
          alt="Dark"
          style={{ width: "20px", height: "20px" }}
          className="lightDarkIcon"
        />
        Dark
      </button>
    </div>
  );
};

export default ThemeToggle;
