import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  devIndicators: false,
  // Demo previews are served through a proxy host, so the action CSRF check
  // needs it allow-listed alongside localhost.
  allowedDevOrigins: ["*.preview.devinapps.com"],
  experimental: {
    serverActions: {
      allowedOrigins: ["localhost:3000", "*.preview.devinapps.com"],
    },
  },
};

export default nextConfig;
