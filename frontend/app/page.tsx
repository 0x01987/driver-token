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

export default function Home() {
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
        <aside className="panel stack">
          <h1>Claim Center</h1>
          <div className="metric">
            <span className="muted">Uber</span>
            <strong>Connected</strong>
          </div>
          <div className="metric">
            <span className="muted">Wallet</span>
            <strong>Not linked</strong>
          </div>
          <div className="metric">
            <span className="muted">Claimable</span>
            <strong>20 DRIVE</strong>
          </div>
          <button className="secondary">Connect Uber</button>
        </aside>

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
