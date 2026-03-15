module.exports = {
  root: true,
  env: {
    browser: true,
    es2022: true,
    node: true,
  },
  parser: "@typescript-eslint/parser",
  parserOptions: {
    ecmaVersion: "latest",
    sourceType: "module",
    ecmaFeatures: {
      jsx: true,
    },
  },
  plugins: ["@typescript-eslint", "react-hooks", "react-refresh", "security"],
  extends: [
    "eslint:recommended",
    "plugin:@typescript-eslint/recommended",
    "plugin:react-hooks/recommended",
    // TODO: ESLint v9 + flat config (eslint.config.js) 移行時は recommended-legacy → recommended に変更し
    //       eslint-plugin-security も最新版にアップグレードする
    "plugin:security/recommended-legacy",
  ],
  ignorePatterns: ["dist", "node_modules"],
  rules: {
    "react-refresh/only-export-components": [
      "warn",
      { allowConstantExport: true },
    ],
    // Node.js 専用ルール: ブラウザSPAには非該当
    "security/detect-non-literal-require": "off",
    "security/detect-non-literal-fs-filename": "off",
    "security/detect-child-process": "off",
    "security/detect-no-csrf-before-method-override": "off",
    "security/detect-buffer-noassert": "off",
    "security/detect-new-buffer": "off",
    "security/detect-pseudoRandomBytes": "off",
    // TypeScript/React のブラケット記法で大量誤検知
    "security/detect-object-injection": "off",
  },
};
