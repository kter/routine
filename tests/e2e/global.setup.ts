import { test as setup, expect } from "@playwright/test";
import fs from "node:fs";
import path from "node:path";
import { AUTH_FILE } from "../../playwright.config";

function readEnvValue(name: string): string | undefined {
  const envPath = path.resolve(__dirname, "../../frontend/.env.local");
  if (!fs.existsSync(envPath)) {
    return undefined;
  }

  const line = fs
    .readFileSync(envPath, "utf8")
    .split(/\r?\n/)
    .find((entry) => entry.startsWith(`${name}=`));

  if (!line) {
    return undefined;
  }

  return line.slice(name.length + 1);
}

const EMAIL = process.env.E2E_TEST_USER_EMAIL ?? readEnvValue("E2E_TEST_USER_EMAIL") ?? "takahashi@tomohiko.io";
const PASSWORD = process.env.E2E_TEST_USER_PASSWORD ?? readEnvValue("E2E_TEST_USER_PASSWORD") ?? "";

setup("dev環境へのログインとセッション保存", async ({ page }) => {
  await page.goto("/login");
  await expect(page.getByRole("heading", { name: "RoutineOps" })).toBeVisible();

  await page.locator('input[name="email"]').fill(EMAIL);
  await page.locator('input[name="password"]').fill(PASSWORD);
  await page.getByRole("button", { name: "ログイン" }).click();

  await expect(page).toHaveURL("/");
  await expect(page.getByRole("button", { name: "ログアウト" })).toBeVisible({ timeout: 15000 });
  await expect(page.getByRole("link", { name: "タスク管理" })).toBeVisible({ timeout: 15000 });

  await page.context().storageState({ path: AUTH_FILE });
});
