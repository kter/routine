import { describe, expect, it } from "vitest";
import { loginSchema } from "./login";

describe("loginSchema", () => {
  it("requires a valid email and minimum password length", () => {
    const result = loginSchema.safeParse({
      email: "invalid-email",
      password: "short",
    });

    expect(result.success).toBe(false);
  });
});
