"use client";

import { FormEvent, useEffect, useState } from "react";

const claimableRides = [
  {
    id: "ride_01",
    platform: "Uber",
    completedAt: "Today, 9:42 AM",
    distance: "18.4 mi",
    duration: "31 min",
    tokens: 10
  },
  {
    id: "ride_02",
    platform: "Uber",
    completedAt: "Yesterday, 6:15 PM",
    distance: "7.8 mi",
    duration: "19 min",
    tokens: 10
  }
];

type DriverSession = {
  access_token: string;
  user_id: string;
  email: string;
};

export default function Home() {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "https://driver-token-api.onrender.com";
  const [session, setSession] = useState<DriverSession | null>(null);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [authMode, setAuthMode] = useState<"login" | "signup">("login");
  const [authError, setAuthError] = useState("");
  const uberConnectUrl = `${apiUrl}/oauth/uber/start?user_id=${encodeURIComponent(session?.user_id || "demo")}`;

  useEffect(() => {
    const saved = window.localStorage.getItem("driver-token-session");
    if (saved) {
      setSession(JSON.parse(saved));
    }
  }, []);

  async function submitAuth(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setAuthError("");

    const response = await fetch(`${apiUrl}/auth/${authMode}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password })
    });

    if (!response.ok) {
      const payload = await response.json().catch(() => ({ detail: "Login failed" }));
      setAuthError(payload.detail || "Login failed");
      return;
    }

    const nextSession = (await response.json()) as DriverSession;
    window.localStorage.setItem("driver-token-session", JSON.stringify(nextSession));
    setSession(nextSession);
  }

  function logout() {
    window.localStorage.removeItem("driver-token-session");
    setSession(null);
  }

  return (
    <main className="shell">
      <header className="topbar">
        <div>
          <div className="brand">Driver Token</div>
          <div className="muted">Verified ride rewards</div>
        </div>
        <button>Connect Wallet</button>
      </header>

      <section className="grid">
        {session ? (
          <aside className="panel stack">
            <h1>Claim Center</h1>
            <div className="metric">
              <span className="muted">Driver</span>
              <strong>{session.email}</strong>
            </div>
            <div className="metric">
              <span className="muted">Uber</span>
              <strong>Not connected</strong>
            </div>
            <div className="metric">
              <span className="muted">Wallet</span>
              <strong>Not linked</strong>
            </div>
            <div className="metric">
              <span className="muted">Claimable</span>
              <strong>20 DRIVE</strong>
            </div>
            <a className="button-link secondary" href={uberConnectUrl}>
              Connect Uber
            </a>
            <button className="secondary" onClick={logout}>
              Log Out
            </button>
          </aside>
        ) : (
          <aside className="panel stack">
            <h1>Driver Login</h1>
            <form className="stack" onSubmit={submitAuth}>
              <label>
                <span className="muted">Email</span>
                <input value={email} onChange={(event) => setEmail(event.target.value)} type="email" required />
              </label>
              <label>
                <span className="muted">Password</span>
                <input
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  type="password"
                  minLength={8}
                  required
                />
              </label>
              {authError ? <div className="error">{authError}</div> : null}
              <button type="submit">{authMode === "login" ? "Log In" : "Create Account"}</button>
            </form>
            <button className="secondary" onClick={() => setAuthMode(authMode === "login" ? "signup" : "login")}>
              {authMode === "login" ? "Create Driver Account" : "Use Existing Account"}
            </button>
          </aside>
        )}

        <section className="stack">
          {claimableRides.map((ride) => (
            <article className="ride" key={ride.id}>
              <div>
                <strong>{ride.platform} completed ride</strong>
                <div className="muted">
                  {ride.completedAt} · {ride.distance} · {ride.duration}
                </div>
              </div>
              <button>Claim {ride.tokens} DRIVE</button>
            </article>
          ))}
        </section>
      </section>
    </main>
  );
}
