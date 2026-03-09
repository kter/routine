import { defineConfig, devices } from "@playwright/test";
import * as path from "path";

const BASE_URL = "https://routine.dev.devtools.site";
export const AUTH_FILE = path.join(__dirname, ".playwright-cli/dev-auth.json");

export default defineConfig({
  testDir: "./tests/e2e",
  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: 1,
  reporter: [["list"], ["html", { outputFolder: "tests/e2e/report", open: "never" }]],
  use: {
    baseURL: BASE_URL,
    trace: "on-first-retry",
    screenshot: "only-on-failure",
  },
  projects: [
    // Setup: ログインしてセッションを保存
    {
      name: "setup",
      testMatch: /global\.setup\.ts/,
    },
    // E2E テスト（setup後に実行）
    {
      name: "chromium",
      use: {
        ...devices["Desktop Chrome"],
        storageState: AUTH_FILE,
      },
      dependencies: ["setup"],
    },
  ],
});
