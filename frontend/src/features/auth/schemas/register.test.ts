import { describe, expect, it } from "vitest";
import { confirmSchema, signUpSchema } from "./register";

describe("signUpSchema", () => {
  it("requires matching passwords", () => {
    const result = signUpSchema.safeParse({
      email: "user@example.com",
      password: "Password1",
      confirmPassword: "Password2",
    });

    expect(result.success).toBe(false);
  });
});

describe("confirmSchema", () => {
  it("requires a confirmation code", () => {
    const result = confirmSchema.safeParse({ code: "" });

    expect(result.success).toBe(false);
  });
});
