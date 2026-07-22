import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

// API calls use relative URLs and are proxied to the backend
// (VITE_API_PROXY_TARGET is set by docker-compose; defaults to a local uvicorn).
export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    port: 5173,
    // Poll for changes: macOS→Linux bind mounts don't propagate inotify events,
    // so without this the dev server never sees edited files inside Docker.
    watch: { usePolling: true, interval: 300 },
    proxy: {
      "/api": {
        target: process.env.VITE_API_PROXY_TARGET ?? "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
});
