import { test, expect } from "@playwright/test";

/**
 * 認証フローのE2Eテスト
 * - 未認証ユーザーのリダイレクト
 * - 誤ったパスワードでのログイン失敗
 * - 正常ログインとログアウト
 */

// 認証不要のテスト（ストレージステートを使わない）
test.use({ storageState: { cookies: [], origins: [] } });

test.describe("認証フロー", () => {
  test("未認証でダッシュボードにアクセスするとログインページへリダイレクト", async ({ page }) => {
    await page.goto("/");
    await expect(page).toHaveURL("/login");
    await expect(page.getByRole("heading", { name: "RoutineOps" })).toBeVisible();
    await expect(page.getByText("定期作業トラッカー")).toBeVisible();
  });

  test("未認証でタスクページにアクセスするとログインページへリダイレクト", async ({ page }) => {
    await page.goto("/tasks");
    await expect(page).toHaveURL("/login");
  });

  test("誤ったパスワードでログインするとエラーが表示される", async ({ page }) => {
    await page.goto("/login");

    await page.locator('input[name="email"]').fill("takahashi@tomohiko.io");
    await page.locator('input[name="password"]').fill("wrongpassword123");
    await page.getByRole("button", { name: "ログイン" }).click();

    // エラーメッセージが表示されることを確認
    await expect(page.getByText(/ログインに失敗|Incorrect username or password/i)).toBeVisible({ timeout: 10000 });
    // ログインページに留まることを確認
    await expect(page).toHaveURL("/login");
  });

  test("バリデーション: 無効なメールアドレスでフォームが送信されない", async ({ page }) => {
    await page.goto("/login");

    // HTML5のemail validationがある場合はブラウザが弾く
    // JavaScriptバリデーションを確認するには空のemailを使う
    await page.locator('input[name="email"]').fill("");
    await page.locator('input[name="password"]').fill("password123");

    // HTMLのrequired/emailバリデーションがブロックするため、submitでページ遷移しないことを確認
    await page.getByRole("button", { name: "ログイン" }).click();

    // ログインページに留まることを確認
    await expect(page).toHaveURL("/login");
    // エラーメッセージ（React側 or ブラウザ側）により送信されないことが重要
  });

  test("バリデーション: パスワードが短すぎるとエラーが表示される", async ({ page }) => {
    await page.goto("/login");

    await page.locator('input[name="email"]').fill("test@example.com");
    await page.locator('input[name="password"]').fill("short");
    await page.getByRole("button", { name: "ログイン" }).click();

    await expect(page.getByText("パスワードは8文字以上で入力してください")).toBeVisible();
  });

  test("正常ログインでダッシュボードへ遷移し、ログアウトできる", async ({ page }) => {
    await page.goto("/login");

    const email = process.env.E2E_TEST_USER_EMAIL ?? "takahashi@tomohiko.io";
    const password = process.env.E2E_TEST_USER_PASSWORD ?? "";

    await page.locator('input[name="email"]').fill(email);
    await page.locator('input[name="password"]').fill(password);
    await page.getByRole("button", { name: "ログイン" }).click();

    // ダッシュボードへ遷移
    await expect(page).toHaveURL("/", { timeout: 15000 });
    await expect(page.getByRole("heading", { name: "ダッシュボード" })).toBeVisible({ timeout: 10000 });

    // ユーザーメール表示確認
    await expect(page.getByText(email)).toBeVisible();

    // ログアウト
    await page.getByRole("button", { name: "ログアウト" }).click();

    // ログインページへリダイレクト
    await expect(page).toHaveURL("/login", { timeout: 10000 });
  });

  test("ログイン済みでログインページにアクセスするとダッシュボードへリダイレクト", async ({ page, context }) => {
    // まずログイン
    await page.goto("/login");
    const email = process.env.E2E_TEST_USER_EMAIL ?? "takahashi@tomohiko.io";
    const password = process.env.E2E_TEST_USER_PASSWORD ?? "";
    await page.locator('input[name="email"]').fill(email);
    await page.locator('input[name="password"]').fill(password);
    await page.getByRole("button", { name: "ログイン" }).click();
    await expect(page).toHaveURL("/", { timeout: 15000 });

    // ログイン後に再度ログインページへアクセス
    await page.goto("/login");
    await expect(page).toHaveURL("/");
  });
});
