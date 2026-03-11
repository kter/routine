import { test, expect } from "@playwright/test";

test.describe("デプロイ後スモーク", () => {
  test("ログイン済みでダッシュボードAPIが200を返し、主要UIが表示される", async ({ page }) => {
    const dashboardResponse = page.waitForResponse((response) => {
      return response.url().includes("/api/v1/dashboard") && response.request().method() === "GET";
    });

    await page.goto("/");

    const response = await dashboardResponse;
    expect(response.status()).toBe(200);

    await expect(page.getByRole("heading", { name: "ダッシュボード" })).toBeVisible({
      timeout: 15000,
    });
    await expect(page.getByText("本日のタスク", { exact: true })).toBeVisible();
    await expect(page.getByText("今後7日間")).toBeVisible();
  });
});
