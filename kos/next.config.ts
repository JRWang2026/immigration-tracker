import type { NextConfig } from "next";

const isProd = process.env.NODE_ENV === "production";
// GitHub Pages project site subpath; empty for local dev
const basePath = process.env.NEXT_PUBLIC_BASE_PATH || "";

const nextConfig: NextConfig = {
  output: "export",
  trailingSlash: true,
  basePath: isProd ? basePath : "",
  // Static export needs assetPrefix when basePath is set
  assetPrefix: isProd ? basePath : "",
  // Let client code read basePath at runtime (for fetch / polling)
  env: {
    NEXT_PUBLIC_BASE_PATH: basePath,
  },
};

export default nextConfig;
