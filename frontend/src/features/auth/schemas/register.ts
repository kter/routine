import { z } from "zod";

export const signUpSchema = z
  .object({
    email: z.string().email("有効なメールアドレスを入力してください"),
    password: z
      .string()
      .min(8, "パスワードは8文字以上で入力してください")
      .regex(/[A-Z]/, "大文字を含めてください")
      .regex(/[a-z]/, "小文字を含めてください")
      .regex(/[0-9]/, "数字を含めてください"),
    confirmPassword: z.string(),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: "パスワードが一致しません",
    path: ["confirmPassword"],
  });

export const confirmSchema = z.object({
  code: z.string().min(1, "確認コードを入力してください"),
});

export type SignUpValues = z.infer<typeof signUpSchema>;
export type ConfirmValues = z.infer<typeof confirmSchema>;
