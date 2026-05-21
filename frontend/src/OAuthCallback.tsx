import { useEffect } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { useAuth } from "./AuthContext";

export function OAuthCallback() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { login } = useAuth();

  useEffect(() => {
    const token = searchParams.get("token");
    if (token) {
      login(token);
      navigate("/", { replace: true });
    } else {
      navigate("/login?error=no_token_provided", { replace: true });
    }
  }, [searchParams, login, navigate]);

  return (
    <div style={{ display: "flex", justifyContent: "center", alignItems: "center", minHeight: "100vh", flexDirection: "column", gap: "1rem" }}>
      <div className="spinner" aria-hidden="true" />
      <h2 style={{ margin: 0 }}>Completing sign-in...</h2>
      <p style={{ color: "#647588", margin: 0 }}>Please wait while we log you in.</p>
    </div>
  );
}
