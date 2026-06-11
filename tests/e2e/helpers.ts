import { expect, type Page } from "@playwright/test";
import fs from "node:fs";
import path from "node:path";

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

export const E2E_EMAIL =
  process.env.E2E_TEST_USER_EMAIL ?? readEnvValue("E2E_TEST_USER_EMAIL") ?? "takahashi@tomohiko.io";
export const E2E_PASSWORD =
  process.env.E2E_TEST_USER_PASSWORD ?? readEnvValue("E2E_TEST_USER_PASSWORD") ?? "";

/** タスク詳細画面からタスクを削除する（テストデータ掃除用）。 */
export async function deleteTask(page: Page, taskId: string): Promise<void> {
  await page.goto(`/tasks/${taskId}`);
  const deleteButton = page.locator(
    "button.border-destructive, button[class*='border-destructive']",
  );
  if ((await deleteButton.count()) > 0) {
    await deleteButton.click();
    await page.getByRole("button", { name: "削除" }).click();
    await expect(page).toHaveURL("/tasks", { timeout: 10000 });
  }
}
