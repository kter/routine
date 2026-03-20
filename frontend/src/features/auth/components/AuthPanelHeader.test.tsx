import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import { AuthPanelHeader } from "./AuthPanelHeader";

describe("AuthPanelHeader", () => {
  it("renders the provided title and eyebrow", () => {
    const html = renderToStaticMarkup(
      <AuthPanelHeader
        title="アカウント作成"
        eyebrow="Cognito User Registration"
      />,
    );

    expect(html).toContain("アカウント作成");
    expect(html).toContain("Cognito User Registration");
  });
});
