import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import { AuthScreenFrame } from "./AuthScreenFrame";

describe("AuthScreenFrame", () => {
  it("renders auth chrome and provided content", () => {
    const html = renderToStaticMarkup(
      <AuthScreenFrame>
        <div>login-form</div>
      </AuthScreenFrame>,
    );

    expect(html).toContain("RoutineOps");
    expect(html).toContain("Secure · AWS Cognito");
    expect(html).toContain("login-form");
  });
});
