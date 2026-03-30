import { useState } from "react";
import { useAuth } from "../../hooks/useAuth";
import api from "../../api/axios";
import "../../styles/auth.css";

export default function Auth() {
  const [isToggled, setIsToggled] = useState(false);
  const [loading, setLoading] = useState(false);

  const { login } = useAuth();

  const [loginData, setLoginData] = useState({
    username: "",
    password: "",
  });

  const [registerData, setRegisterData] = useState({
    role: "STUDENT",
    username: "",
    password: "",
    name: "",
    roll_number: "",
    department: "",
    year: "",
    designation: "",
  });

  // ================= LOGIN =================
  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const res = await api.post("/auth/login/", loginData);

      if (!res.data?.access || !res.data?.refresh || !res.data?.user) {
        alert("Invalid login response.");
        return;
      }

      login(res.data);

    } catch (err) {
      alert("Invalid credentials.");
    } finally {
      setLoading(false);
    }
  };

  // ================= REGISTER =================
  const handleRegister = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const endpoint =
        registerData.role === "STUDENT"
          ? "/register/student/"
          : "/register/faculty/";

      let payload =
        registerData.role === "STUDENT"
          ? {
              username: registerData.username,
              password: registerData.password,
              name: registerData.name,
              roll_number: registerData.roll_number,
              department: registerData.department,
              year: Number(registerData.year),
            }
          : {
              username: registerData.username,
              password: registerData.password,
              name: registerData.name,
              department: registerData.department,
              designation: registerData.designation,
            };

      await api.post(endpoint, payload);

      alert("Registration successful. Please login.");

      // Reset register form
      setRegisterData({
        role: "STUDENT",
        username: "",
        password: "",
        name: "",
        roll_number: "",
        department: "",
        year: "",
        designation: "",
      });

      setIsToggled(false);

    }catch (err) {
  console.log("BACKEND ERROR:", err.response?.data);
  alert(JSON.stringify(err.response?.data));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className={`auth-wrapper ${isToggled ? "toggled" : ""}`}>

        {/* LOGIN */}
        <div className="credentials-panel signin">
          <h2>Login</h2>

          <form onSubmit={handleLogin}>
            <input
              type="text"
              placeholder="Username / Register No"
              required
              value={loginData.username}
              onChange={(e) =>
                setLoginData({ ...loginData, username: e.target.value })
              }
            />

            <input
              type="password"
              placeholder="Password"
              required
              value={loginData.password}
              onChange={(e) =>
                setLoginData({ ...loginData, password: e.target.value })
              }
            />

            <button type="submit" disabled={loading}>
              {loading ? "Please wait..." : "Login"}
            </button>
          </form>

          <p onClick={() => setIsToggled(true)}>Sign Up</p>
        </div>

        {/* REGISTER */}
        <div className="credentials-panel signup">
          <h2>Register</h2>

          <form onSubmit={handleRegister}>
            <select
              value={registerData.role}
              onChange={(e) =>
                setRegisterData({ ...registerData, role: e.target.value })
              }
            >
              <option value="STUDENT">Student</option>
              <option value="FACULTY">Faculty</option>
            </select>

            <input
              type="text"
              placeholder={
                registerData.role === "STUDENT"
                  ? "Register No"
                  : "Username"
              }
              required
              value={registerData.username}
              onChange={(e) =>
                setRegisterData({ ...registerData, username: e.target.value })
              }
            />

            <input
              type="text"
              placeholder="Full Name"
              required
              value={registerData.name}
              onChange={(e) =>
                setRegisterData({ ...registerData, name: e.target.value })
              }
            />

            {registerData.role === "STUDENT" && (
              <>
                <input
                  type="text"
                  placeholder="Roll Number"
                  required
                  value={registerData.roll_number}
                  onChange={(e) =>
                    setRegisterData({
                      ...registerData,
                      roll_number: e.target.value,
                    })
                  }
                />

                <input
                  type="text"
                  placeholder="Department"
                  required
                  value={registerData.department}
                  onChange={(e) =>
                    setRegisterData({
                      ...registerData,
                      department: e.target.value,
                    })
                  }
                />

                <input
                  type="number"
                  placeholder="Year"
                  required
                  value={registerData.year}
                  onChange={(e) =>
                    setRegisterData({
                      ...registerData,
                      year: e.target.value,
                    })
                  }
                />
              </>
            )}

            {registerData.role === "FACULTY" && (
              <>
                <input
                  type="text"
                  placeholder="Department"
                  required
                  value={registerData.department}
                  onChange={(e) =>
                    setRegisterData({
                      ...registerData,
                      department: e.target.value,
                    })
                  }
                />

                <input
                  type="text"
                  placeholder="Designation"
                  required
                  value={registerData.designation}
                  onChange={(e) =>
                    setRegisterData({
                      ...registerData,
                      designation: e.target.value,
                    })
                  }
                />
              </>
            )}

            <input
              type="password"
              placeholder="Password"
              required
              value={registerData.password}
              onChange={(e) =>
                setRegisterData({
                  ...registerData,
                  password: e.target.value,
                })
              }
            />

            <button type="submit" disabled={loading}>
              {loading ? "Please wait..." : "Register"}
            </button>
          </form>

          <p onClick={() => setIsToggled(false)}>Sign In</p>
        </div>
      </div>
    </div>
  );
}