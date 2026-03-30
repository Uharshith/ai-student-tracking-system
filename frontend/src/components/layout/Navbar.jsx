import { useAuth } from "../../hooks/useAuth";

export default function Navbar() {
  const { user, logout } = useAuth();

  return (
    <div className="navbar">
      <div>
        Welcome, <strong>{user?.username}</strong>
      </div>
      <button onClick={logout}>Logout</button>
    </div>
  );
}