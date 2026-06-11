import { test as setup, expect } from "@playwright/test";
import { AUTH_FILE } from "../../playwright.config";
import { E2E_EMAIL, E2E_PASSWORD } from "./helpers";

setup("dev環境へのログインとセッション保存", async ({ page }) => {
  await page.goto("/login");
  await expect(page.getByRole("heading", { name: "RoutineOps" })).toBeVisible();

  await page.locator('input[name="email"]').fill(E2E_EMAIL);
  await page.locator('input[name="password"]').fill(E2E_PASSWORD);
  await page.getByRole("button", { name: "ログイン" }).click();

  await expect(page).toHaveURL("/");
  await expect(page.getByRole("button", { name: "ログアウト" })).toBeVisible({ timeout: 15000 });
  await expect(page.getByRole("link", { name: "タスク管理" })).toBeVisible({ timeout: 15000 });

  await page.context().storageState({ path: AUTH_FILE });
});
