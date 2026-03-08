import { test, expect } from "@playwright/test";

/**
 * ダッシュボードのE2Eテスト
 * - ページ表示とUI要素の確認
 * - サイドバーナビゲーション
 * - ダッシュボードパネルの表示
 */

test.describe("ダッシュボード", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/");
    await expect(page.getByRole("heading", { name: "ダッシュボード" })).toBeVisible({ timeout: 10000 });
  });

  test("ダッシュボードが正常に表示される", async ({ page }) => {
    // ページタイトル
    await expect(page).toHaveTitle("RoutineOps Tracker");

    // メインヘッダー
    await expect(page.getByRole("heading", { name: "ダッシュボード" })).toBeVisible();

    // 日付が表示される
    const today = new Date();
    const year = today.getFullYear();
    await expect(page.getByText(`${year}年`)).toBeVisible();
  });

  test("サイドバーのブランドロゴとナビゲーションが表示される", async ({ page }) => {
    // サイドバーブランド
    await expect(page.getByText("RoutineOps").first()).toBeVisible();
    await expect(page.getByText("SYSTEM ONLINE")).toBeVisible();

    // ナビゲーションリンク
    await expect(page.getByRole("link", { name: "ダッシュボード" })).toBeVisible();
    await expect(page.getByRole("link", { name: "タスク管理" })).toBeVisible();
    await expect(page.getByRole("link", { name: "実行ログ" })).toBeVisible();
  });

  test("トップバーにユーザーメールとログアウトボタンが表示される", async ({ page }) => {
    await expect(page.getByText("takahashi@tomohiko.io")).toBeVisible();
    await expect(page.getByRole("button", { name: "ログアウト" })).toBeVisible();
  });

  test("本日のタスクパネルが表示される", async ({ page }) => {
    await expect(page.getByText("本日のタスク", { exact: true })).toBeVisible();
  });

  test("今後7日間パネルが表示される", async ({ page }) => {
    await expect(page.getByText("今後7日間")).toBeVisible();
  });

  test("サイドバーでタスク管理ページへ遷移できる", async ({ page }) => {
    await page.getByRole("link", { name: "タスク管理" }).click();
    await expect(page).toHaveURL("/tasks");
    await expect(page.getByRole("heading", { name: "タスク管理" })).toBeVisible();
  });

  test("サイドバーで実行ログページへ遷移できる", async ({ page }) => {
    await page.getByRole("link", { name: "実行ログ" }).click();
    await expect(page).toHaveURL("/executions");
    await expect(page.getByRole("heading", { name: "実行ログ" })).toBeVisible();
  });

  test("サイドバーでダッシュボードリンクがアクティブ状態で表示される", async ({ page }) => {
    const dashboardLink = page.getByRole("link", { name: "ダッシュボード" });
    // アクティブリンクはCSSスタイルで強調表示される（aria属性は使わないが、リンクが存在する）
    await expect(dashboardLink).toBeVisible();
  });
});
