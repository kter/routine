import { test, expect, type Page } from "@playwright/test";
import { deleteTask } from "./helpers";

/**
 * 実行ウィザードのE2Eテスト（完走・スキップ・中断フロー）
 * - 証跡テキスト入力 → ステップ完了
 * - 任意ステップのスキップ
 * - 全ステップ完了後の実行完了
 * - 実行の中断
 */

const WIZARD_TASK_TITLE = `E2E_ウィザード_${Date.now()}`;

/**
 * 必須テキスト証跡ステップ + 任意（証跡なし）ステップを持つタスクを作成し、taskId を返す。
 */
async function createWizardTask(page: Page, title: string): Promise<string> {
  await page.goto("/tasks/new");
  await expect(page.getByRole("heading", { name: "タスクを作成" })).toBeVisible();

  await page.locator('input[name="title"]').fill(title);
  await page.locator('input[name="estimatedMinutes"]').fill("15");

  // ステップ1: 必須・テキスト証跡
  await page.getByRole("button", { name: "ステップを追加" }).click();
  await page.locator('input[placeholder="ステップタイトル"]').nth(0).fill("必須テキスト確認");
  await page.locator("select").nth(0).selectOption("text");

  // ステップ2: 任意・証跡なし
  await page.getByRole("button", { name: "ステップを追加" }).click();
  await page.locator('input[placeholder="ステップタイトル"]').nth(1).fill("任意ステップ");
  await page.locator('input[type="checkbox"]').nth(1).uncheck();

  await page.getByRole("button", { name: "作成" }).click();
  await page.waitForURL(/\/tasks\/[0-9a-f-]+/, { timeout: 15000 });
  return page.url().split("/tasks/")[1];
}

/** タスク詳細から実行を開始し、実行ページへの遷移を待つ。 */
async function startExecution(page: Page, taskId: string): Promise<void> {
  await page.goto(`/tasks/${taskId}`);
  await expect(page.getByRole("button", { name: "実行" })).toBeVisible({ timeout: 10000 });
  await page.getByRole("button", { name: "実行" }).click();
  await expect(page).toHaveURL(/\/executions\/[0-9a-f-]+/, { timeout: 15000 });
}

test.describe("実行ウィザード", () => {
  let taskId: string;

  test.beforeAll(async ({ browser }) => {
    const page = await browser.newPage();
    taskId = await createWizardTask(page, WIZARD_TASK_TITLE);
    await page.close();
  });

  test.afterAll(async ({ browser }) => {
    if (!taskId) return;
    const page = await browser.newPage();
    try {
      await deleteTask(page, taskId);
    } catch {
      // cleanup failure is not critical
    }
    await page.close();
  });

  test("証跡テキストを入力してステップを完了し、実行を完走できる", async ({ page }) => {
    await startExecution(page, taskId);

    // ステップ1: 証跡テキストなしでは完了ボタンが無効
    await expect(page.getByText("必須テキスト確認")).toBeVisible({ timeout: 10000 });
    const completeButton = page.getByRole("button", { name: "完了", exact: true });
    await expect(completeButton).toBeDisabled();

    // 証跡テキストを入力すると完了できる
    await page
      .locator('textarea[placeholder="実施内容や確認結果を入力してください"]')
      .fill("E2E: 確認完了。問題なし。");
    await expect(completeButton).toBeEnabled();
    await completeButton.click();

    // ステップ2（任意）が表示され、スキップできる
    await expect(page.getByText("任意ステップ")).toBeVisible({ timeout: 10000 });
    await page.getByRole("button", { name: "スキップ" }).click();

    // 全ステップ完了 → 実行完了
    await expect(page.getByText("全ステップが完了しました。実行を完了してください。")).toBeVisible({
      timeout: 10000,
    });
    await page.getByRole("button", { name: "実行完了" }).click();

    // ステータスバッジが「完了」になる
    await expect(page.getByText("完了", { exact: true })).toBeVisible({ timeout: 10000 });
  });

  test("必須ステップにはスキップボタンが表示されない", async ({ page }) => {
    await startExecution(page, taskId);

    await expect(page.getByText("必須テキスト確認")).toBeVisible({ timeout: 10000 });
    await expect(page.getByRole("button", { name: "スキップ" })).toHaveCount(0);

    // 後続テストのため中断しておく
    await page.getByRole("button", { name: "中断" }).click();
    await page.getByRole("button", { name: "中断する" }).click();
    await expect(page.getByText("中断", { exact: true })).toBeVisible({ timeout: 10000 });
  });

  test("実行を中断するとステータスが中断になる", async ({ page }) => {
    await startExecution(page, taskId);

    // 中断 → 確認ダイアログ → 中断する
    await page.getByRole("button", { name: "中断" }).click();
    await expect(page.getByText("実行を中断しますか？")).toBeVisible({ timeout: 5000 });
    await expect(page.getByText("中断後は再開できません")).toBeVisible();
    await page.getByRole("button", { name: "中断する" }).click();

    // ステータスバッジが「中断」になり、ステップ入力UIが消える
    await expect(page.getByText("中断", { exact: true })).toBeVisible({ timeout: 10000 });
    await expect(
      page.locator('textarea[placeholder="実施内容や確認結果を入力してください"]'),
    ).toHaveCount(0);
  });

  test("中断ダイアログをキャンセルすると実行が継続される", async ({ page }) => {
    await startExecution(page, taskId);

    await page.getByRole("button", { name: "中断" }).click();
    await expect(page.getByText("実行を中断しますか？")).toBeVisible({ timeout: 5000 });
    await page.getByRole("button", { name: "キャンセル" }).click();

    // 実行中のまま、ステップ入力UIが残っている
    await expect(page.getByText("実行中")).toBeVisible();
    await expect(page.getByText("必須テキスト確認")).toBeVisible();

    // 後続テストのため中断しておく
    await page.getByRole("button", { name: "中断" }).click();
    await page.getByRole("button", { name: "中断する" }).click();
    await expect(page.getByText("中断", { exact: true })).toBeVisible({ timeout: 10000 });
  });
});
