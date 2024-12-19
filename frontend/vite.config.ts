import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    host: true, // This exposes the server to your network
    port: 3000, // Optional: specify port
  },
});
