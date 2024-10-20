import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      // This alias ensures compatibility with pdfjs-dist if needed
      "pdfjs-dist/build/pdf.worker.min.js": "pdfjs-dist/build/pdf.worker.js",
    },
  },
});
