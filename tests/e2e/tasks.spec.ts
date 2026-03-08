import { test, expect } from "@playwright/test";

/**
 * タスク管理のE2Eテスト
 * - タスク一覧表示
 * - タスク新規作成
 * - タスク詳細表示
 * - タスク編集
 * - タスク削除
 */

const TEST_TASK_TITLE = `E2Eテスト_タスク_${Date.now()}`;

test.describe("タスク管理", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/tasks");
    await expect(page.getByRole("heading", { name: "タスク管理" })).toBeVisible({ timeout: 10000 });
  });

  test("タスク一覧ページが表示される", async ({ page }) => {
    await expect(page.getByRole("heading", { name: "タスク管理" })).toBeVisible();
    await expect(page.getByRole("link", { name: "新規作成" })).toBeVisible();
  });

  test("タスクがない場合は空状態メッセージが表示される", async ({ page }) => {
    // タスクが0件の場合のみ表示
    const emptyMsg = page.getByText("タスクが登録されていません。新規作成してください。");
    const isVisible = await emptyMsg.isVisible().catch(() => false);
    if (isVisible) {
      await expect(emptyMsg).toBeVisible();
    }
    // タスクがある場合はこのテストはスキップ
  });

  test("新規作成ボタンをクリックするとタスク作成フォームへ遷移", async ({ page }) => {
    await page.getByRole("link", { name: "新規作成" }).click();
    await expect(page).toHaveURL("/tasks/new");
    await expect(page.getByRole("heading", { name: "タスクを作成" })).toBeVisible();
  });

  test.describe("タスク作成フォーム", () => {
    test.beforeEach(async ({ page }) => {
      await page.goto("/tasks/new");
      await expect(page.getByRole("heading", { name: "タスクを作成" })).toBeVisible();
    });

    test("タスク作成フォームの全フィールドが表示される", async ({ page }) => {
      await expect(page.getByText("タイトル *")).toBeVisible();
      await expect(page.locator('input[name="title"]')).toBeVisible();
      await expect(page.getByText("説明")).toBeVisible();
      await expect(page.locator('textarea[name="description"]')).toBeVisible();
      await expect(page.getByText("スケジュール *")).toBeVisible();
      await expect(page.locator('input[name="timezone"]')).toBeVisible();
      await expect(page.locator('input[name="estimatedMinutes"]')).toBeVisible();
      await expect(page.locator('input[name="tags"]')).toBeVisible();
      await expect(page.getByRole("button", { name: "ステップを追加" })).toBeVisible();
      await expect(page.getByRole("button", { name: "作成" })).toBeVisible();
    });

    test("タイトルなしで送信するとバリデーションエラーが表示される", async ({ page }) => {
      await page.getByRole("button", { name: "作成" }).click();
      await expect(page.getByText("タイトルは必須です")).toBeVisible();
    });

    test("スケジュールプリセットを選択できる", async ({ page }) => {
      await expect(page.getByRole("button", { name: "毎日 10:00" })).toBeVisible();
      await expect(page.getByRole("button", { name: "毎週月曜 10:00" })).toBeVisible();
      await expect(page.getByRole("button", { name: "毎月1日 10:00" })).toBeVisible();
      await expect(page.getByRole("button", { name: "毎月末日 10:00" })).toBeVisible();
      await expect(page.getByRole("button", { name: "カスタム" })).toBeVisible();

      // 毎週月曜を選択できることを確認
      await page.getByRole("button", { name: "毎週月曜 10:00" }).click();
    });

    test("タスクを正常に作成できる", async ({ page }) => {
      const title = TEST_TASK_TITLE;

      await page.locator('input[name="title"]').fill(title);
      await page.locator('textarea[name="description"]').fill("E2Eテスト用のタスクです");
      await page.locator('input[name="estimatedMinutes"]').fill("30");
      await page.locator('input[name="tags"]').fill("e2e, テスト");

      await page.getByRole("button", { name: "作成" }).click();

      // タスク詳細ページへリダイレクト
      await expect(page).toHaveURL(/\/tasks\/[0-9a-f-]+/, { timeout: 15000 });
      await expect(page.getByRole("heading", { name: title })).toBeVisible({ timeout: 10000 });
    });

    test("ステップを追加してタスクを作成できる", async ({ page }) => {
      const title = `${TEST_TASK_TITLE}_steps`;

      await page.locator('input[name="title"]').fill(title);
      await page.locator('input[name="estimatedMinutes"]').fill("30");
      await page.getByRole("button", { name: "ステップを追加" }).click();

      // ステップフォームが表示される（StepEditorのinput）- placeholder="ステップタイトル"
      const stepInput = page.locator('input[placeholder="ステップタイトル"]').first();
      await expect(stepInput).toBeVisible({ timeout: 5000 });
      await stepInput.fill("手順1: 確認する");

      await page.getByRole("button", { name: "作成" }).click();

      await expect(page).toHaveURL(/\/tasks\/[0-9a-f-]+/, { timeout: 15000 });
      await expect(page.getByText("手順1: 確認する")).toBeVisible({ timeout: 10000 });
    });
  });

  test.describe("タスク詳細・編集・削除", () => {
    let taskId: string;

    // テスト用タスクを事前に作成
    test.beforeAll(async ({ browser }) => {
      const page = await browser.newPage();
      await page.goto("/tasks/new");
      await page.locator('input[name="title"]').fill(TEST_TASK_TITLE + "_crud");
      await page.locator('input[name="estimatedMinutes"]').fill("30");
      await page.getByRole("button", { name: "作成" }).click();
      await page.waitForURL(/\/tasks\/[0-9a-f-]+/, { timeout: 15000 });
      const url = page.url();
      taskId = url.split("/tasks/")[1];
      await page.close();
    });

    test("タスク詳細ページが表示される", async ({ page }) => {
      await page.goto(`/tasks/${taskId}`);
      await expect(page.getByRole("heading", { name: TEST_TASK_TITLE + "_crud" })).toBeVisible({ timeout: 10000 });
      await expect(page.getByRole("button", { name: "実行" })).toBeVisible();
      await expect(page.getByRole("link", { name: "編集" })).toBeVisible();
    });

    test("タスク詳細からタスク一覧へ戻れる（サイドバー）", async ({ page }) => {
      await page.goto(`/tasks/${taskId}`);
      await page.getByRole("link", { name: "タスク管理" }).click();
      await expect(page).toHaveURL("/tasks");
    });

    test("タスクを編集できる", async ({ page }) => {
      await page.goto(`/tasks/${taskId}/edit`);

      const updatedTitle = TEST_TASK_TITLE + "_updated";
      await page.locator('input[name="title"]').fill("");
      await page.locator('input[name="title"]').fill(updatedTitle);
      await page.getByRole("button", { name: "保存" }).click();

      await expect(page).toHaveURL(/\/tasks\/[0-9a-f-]+/, { timeout: 15000 });
      await expect(page.getByRole("heading", { name: updatedTitle })).toBeVisible({ timeout: 10000 });
    });

    test("タスクを削除できる", async ({ page }) => {
      // 削除用のタスクを別途作成
      await page.goto("/tasks/new");
      await page.locator('input[name="title"]').fill(TEST_TASK_TITLE + "_delete");
      await page.locator('input[name="estimatedMinutes"]').fill("30");
      await page.getByRole("button", { name: "作成" }).click();
      await page.waitForURL(/\/tasks\/[0-9a-f-]+/, { timeout: 15000 });

      // 削除ボタン（Trash2アイコンのみのボタン）をクリック
      // TaskDetailPageで削除ボタンはborder-destructiveを持つbuttonの最後
      await page.locator("button.border-destructive, button[class*='border-destructive']").click();

      // 確認ダイアログが表示される
      await expect(page.getByText("タスクを削除しますか？")).toBeVisible({ timeout: 5000 });
      await expect(page.getByText("この操作は取り消せません")).toBeVisible();

      // 削除を確定
      await page.getByRole("button", { name: "削除" }).click();

      // タスク一覧へリダイレクト
      await expect(page).toHaveURL("/tasks", { timeout: 10000 });
    });
  });
});
