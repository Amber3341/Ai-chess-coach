import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "./AuthContext";
import { updateUser, deleteUser } from "./api";

export function Settings() {
  const { user, logout } = useAuth();
  const [displayName, setDisplayName] = useState(user?.display_name || "");
  const [message, setMessage] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    if (user) setDisplayName(user.display_name ?? "");
  }, [user]);

  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!displayName.trim()) {
      setMessage("Display name cannot be empty.");
      return;
    }
    try {
      await updateUser({ display_name: displayName });
      setMessage("Profile updated successfully.");
    } catch (err) {
      setMessage((err as Error).message);
    }
  };

  const handleDelete = async () => {
    if (!window.confirm("Are you sure you want to delete your account? This action cannot be undone.")) return;
    try {
      await deleteUser();
      await logout();
      navigate("/login", { replace: true });
    } catch (err) {
      setMessage((err as Error).message);
    }
  };

  return (
    <main className="settings-page" style={{ maxWidth: "400px", margin: "2rem auto" }}>
      <h2>Account Settings</h2>
      <form onSubmit={handleUpdate} style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
        <label>
          Display Name:
          <input
            type="text"
            value={displayName}
            onChange={(e) => setDisplayName(e.target.value)}
            placeholder="Enter a display name"
          />
        </label>
        <button type="submit" className="primary">Update Profile</button>
      </form>
      <hr />
      <button onClick={handleDelete} className="danger">Delete Account</button>
      {message && <p style={{ marginTop: "1rem", color: "#e53935" }}>{message}</p>}
    </main>
  );
}
