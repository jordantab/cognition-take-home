import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  devIndicators: false,
  // Demo previews are served through a proxy that forwards its own hostname as
  // `x-forwarded-host` but rewrites `Origin` to `localhost`, so both sides of
  // the server-action CSRF comparison have to be allow-listed.
  allowedDevOrigins: ["*.preview.devinapps.com"],
  experimental: {
    serverActions: {
      allowedOrigins: [
        "localhost",
        "localhost:3000",
        "*.preview.devinapps.com",
      ],
    },
  },
};

export default nextConfig;
