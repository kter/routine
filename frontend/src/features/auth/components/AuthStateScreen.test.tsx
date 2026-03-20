import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import { AuthStateScreen } from "./AuthStateScreen";

describe("AuthStateScreen", () => {
  it("renders the auth frame with status copy", () => {
    const html = renderToStaticMarkup(
      <AuthStateScreen
        title="認証状態を確認中..."
        description="セッションを検証しています。"
      />,
    );

    expect(html).toContain("RoutineOps");
    expect(html).toContain("認証状態を確認中...");
    expect(html).toContain("セッションを検証しています。");
  });
});
