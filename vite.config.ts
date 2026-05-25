import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  base: "/russia-history-timeline/",
  plugins: [react()],
});
