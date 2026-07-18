import { useEffect, useState } from "react";

type ApiStatus = "checking" | "online" | "offline";

interface HealthResponse {
  status: string;
  service: string;
  version: string;
}

const STATUS_LABEL: Record<ApiStatus, string> = {
  checking: "Checking…",
  online: "Online",
  offline: "Offline",
};

function App() {
  const [status, setStatus] = useState<ApiStatus>("checking");
  const [version, setVersion] = useState("");

  useEffect(() => {
    fetch("/api/v1/health")
      .then((res) => res.json() as Promise<HealthResponse>)
      .then((body) => {
        setStatus(body.status === "ok" ? "online" : "offline");
        setVersion(body.version);
      })
      .catch(() => setStatus("offline"));
  }, []);

  return (
    <main className="shell">
      <h1>Cloud ML Platform</h1>
      <p className="tagline">Train, track and deploy machine learning models.</p>
      <div className={`status status-${status}`}>
        <span className="dot" />
        API {STATUS_LABEL[status]}
        {version && ` — v${version}`}
      </div>
      <p className="hint">
        Dashboard under construction — follow the{" "}
        <a href="https://github.com/malo-coet/cloud-ml-platform/blob/main/docs/roadmap.md">
          roadmap
        </a>
        .
      </p>
    </main>
  );
}

export default App;
