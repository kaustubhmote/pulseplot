import { defineConfig } from "@playwright/test";
import { fileURLToPath } from "node:url";

export default defineConfig({
  testDir: "./tests/browser",
  fullyParallel: true,
  workers: process.env.CI ? 2 : undefined,
  reporter: "list",
  use: {
    baseURL: "http://127.0.0.1:4173",
    viewport: { width: 1600, height: 1000 },
    trace: "retain-on-failure",
    launchOptions: {
      executablePath: process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH || undefined
    }
  },
  webServer: {
    command: `"${process.execPath}" scripts/dev.mjs`,
    cwd: fileURLToPath(new URL("./", import.meta.url)),
    url: "http://127.0.0.1:4173/src/index.html",
    env: { PORT: "4173" },
    reuseExistingServer: false
  }
});
