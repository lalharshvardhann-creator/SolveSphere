import React, { createContext, useContext, useState, useEffect } from "react";

const RouterContext = createContext();

export function RouterProvider({ children }) {
  const [currentPath, setCurrentPath] = useState(() => {
    const hash = window.location.hash.replace(/^#/, "");
    return hash || "/";
  });

  useEffect(() => {
    const handleHashChange = () => {
      const hash = window.location.hash.replace(/^#/, "");
      setCurrentPath(hash || "/");
      window.scrollTo(0, 0);
    };

    window.addEventListener("hashchange", handleHashChange);
    return () => window.removeEventListener("hashchange", handleHashChange);
  }, []);

  const navigate = (path) => {
    window.location.hash = path;
    setCurrentPath(path);
    window.scrollTo(0, 0);
  };

  return (
    <RouterContext.Provider value={{ currentPath, navigate }}>
      {children}
    </RouterContext.Provider>
  );
}

export function useLocation() {
  const context = useContext(RouterContext);
  if (!context) {
    throw new Error("useLocation must be used within a RouterProvider");
  }
  return context;
}

export function Link({ to, children, className = "", ...props }) {
  const { navigate, currentPath } = useLocation();
  const isActive = currentPath === to;

  return (
    <a
      href={`#${to}`}
      onClick={(e) => {
        e.preventDefault();
        navigate(to);
      }}
      className={`${className} ${isActive ? "active" : ""}`}
      {...props}
    >
      {children}
    </a>
  );
}
