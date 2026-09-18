import { defineConfig, devices } from "@playwright/test";

const API_PORT = 8100;
const WEB_PORT = 3100;
const API_BASE_URL = `http://127.0.0.1:${API_PORT}`;

/**
 * The golden path runs against the real stack: FastAPI on the seeded SQLite
 * fixture, plus the Next.js app pointed at it. Ports differ from `make dev`
 * so a running dev stack is never disturbed.
 */
export default defineConfig({
  testDir: "./e2e",
  timeout: 60_000,
  expect: { timeout: 10_000 },
  fullyParallel: false,
  workers: 1,
  forbidOnly: !!process.env.CI,
  reporter: process.env.CI ? "github" : "list",
  use: {
    baseURL: `http://localhost:${WEB_PORT}`,
    trace: "on-first-retry",
  },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
  webServer: [
    {
      command: `.venv/bin/uvicorn app.main:app --port ${API_PORT}`,
      cwd: "../api",
      url: `${API_BASE_URL}/api/users`,
      reuseExistingServer: !process.env.CI,
      timeout: 60_000,
    },
    {
      command: `npm run dev -- --port ${WEB_PORT}`,
      url: `http://localhost:${WEB_PORT}/aml`,
      env: { API_BASE_URL },
      reuseExistingServer: !process.env.CI,
      timeout: 120_000,
    },
  ],
});
