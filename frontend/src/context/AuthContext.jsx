import { createContext, useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

export const AuthContext = createContext(null);

export default function AuthProvider({ children }) {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);

  // 🔹 Load user safely from localStorage
  useEffect(() => {
    const storedUser = localStorage.getItem("user");
    const access = localStorage.getItem("access");

    if (!storedUser || !access) return;

    try {
      // prevent "undefined" string crash
      if (storedUser === "undefined") {
        localStorage.removeItem("user");
        return;
      }

      const parsedUser = JSON.parse(storedUser);

      // extra safety check
      if (parsedUser && typeof parsedUser === "object") {
        setUser(parsedUser);
      } else {
        localStorage.removeItem("user");
      }

    } catch (error) {
      console.error("Corrupted user data in localStorage");
      localStorage.removeItem("user");
    }
  }, []);

  // 🔹 Login function
  const login = (data) => {
    if (!data?.access || !data?.refresh || !data?.user) {
      console.error("Invalid login response");
      return;
    }

    try {
      localStorage.setItem("access", data.access);
      localStorage.setItem("refresh", data.refresh);
      localStorage.setItem("user", JSON.stringify(data.user));

      setUser(data.user);

      navigate(data.user.role === "STUDENT" ? "/student" : "/faculty");
    } catch (error) {
      console.error("Failed to store auth data");
    }
  };

  // 🔹 Logout function
  const logout = () => {
    localStorage.removeItem("user");
    localStorage.removeItem("access");
    localStorage.removeItem("refresh");

    setUser(null);
    navigate("/login");
  };

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}