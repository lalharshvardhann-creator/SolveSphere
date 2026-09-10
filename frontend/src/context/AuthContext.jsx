import React, { createContext, useContext, useState, useEffect } from "react";
import { api, getStoredToken, getStoredUser, setStoredToken, setStoredUser } from "../services/api";

const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [user, setUser] = useState(getStoredUser());
  const [token, setToken] = useState(getStoredToken());
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function verifyAuth() {
      const storedToken = getStoredToken();
      if (storedToken) {
        try {
          const profile = await api.auth.getMe();
          setUser(profile);
          setStoredUser(profile);
        } catch (err) {
          // Token expired or invalid
          if (
            err.message &&
            (err.message.includes("401") ||
              err.message.includes("credentials") ||
              err.message.includes("Unauthorized") ||
              err.message.includes("Could not validate"))
          ) {
            setStoredToken(null);
            setStoredUser(null);
            setUser(null);
            setToken(null);
          }
        }
      }
      setLoading(false);
    }
    verifyAuth();
  }, []);

  const login = async (email, password) => {
    const res = await api.auth.login(email, password);
    setToken(res.token);
    setUser(res.user);
    return res;
  };

  const register = async (userData) => {
    const newUser = await api.auth.register(userData);
    // Auto-login after registration
    const res = await api.auth.login(userData.email, userData.password);
    setToken(res.token);
    setUser(res.user);
    return res;
  };

  const logout = () => {
    setStoredToken(null);
    setStoredUser(null);
    setUser(null);
    setToken(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated: !!user && !!token,
        loading,
        login,
        register,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
