import { test as setup, expect } from "@playwright/test";
import { AUTH_FILE } from "../../playwright.config";

const EMAIL = process.env.E2E_TEST_USER_EMAIL ?? "takahashi@tomohiko.io";
const PASSWORD = process.env.E2E_TEST_USER_PASSWORD ?? "";

setup("dev環境へのログインとセッション保存", async ({ page }) => {
  await page.goto("/login");
  await expect(page.getByRole("heading", { name: "RoutineOps" })).toBeVisible();

  await page.locator('input[name="email"]').fill(EMAIL);
  await page.locator('input[name="password"]').fill(PASSWORD);
  await page.getByRole("button", { name: "ログイン" }).click();

  // ダッシュボードへリダイレクト確認
  await expect(page).toHaveURL("/");
  await expect(page.getByRole("heading", { name: "ダッシュボード" })).toBeVisible({ timeout: 15000 });

  // セッション状態を保存
  await page.context().storageState({ path: AUTH_FILE });
});
