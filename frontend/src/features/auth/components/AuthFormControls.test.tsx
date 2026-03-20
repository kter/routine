import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import { AuthFormError } from "./AuthFormError";
import { AuthFormField } from "./AuthFormField";
import { AuthSubmitButton } from "./AuthSubmitButton";

describe("AuthFormField", () => {
  it("forwards refs to the input element for form libraries", () => {
    expect((AuthFormField as unknown as { $$typeof?: symbol }).$$typeof).toBe(
      Symbol.for("react.forward_ref"),
    );
  });

  it("renders label, input, and error text", () => {
    const html = renderToStaticMarkup(
      <AuthFormField
        label="メールアドレス"
        type="email"
        name="email"
        error="必須です"
      />,
    );

    expect(html).toContain("メールアドレス");
    expect(html).toContain('type="email"');
    expect(html).toContain("必須です");
  });
});

describe("AuthFormError", () => {
  it("omits markup when no message is provided", () => {
    expect(renderToStaticMarkup(<AuthFormError message={null} />)).toBe("");
  });
});

describe("AuthSubmitButton", () => {
  it("renders the submitting label when disabled", () => {
    const html = renderToStaticMarkup(
      <AuthSubmitButton
        idleLabel="ログイン"
        submittingLabel="ログイン中..."
        isSubmitting
      />,
    );

    expect(html).toContain("ログイン中...");
    expect(html).toContain("disabled");
  });
});
