import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import { PageSkeleton } from "./PageSkeleton";
import { PageStateMessage } from "./PageStateMessage";

describe("PageSkeleton", () => {
  it("renders configured skeleton blocks", () => {
    const html = renderToStaticMarkup(
      <PageSkeleton
        blocks={[
          { className: "h-5 w-32 rounded shimmer" },
          { className: "h-48 rounded-md shimmer" },
        ]}
      />,
    );

    expect(html).toContain("h-5 w-32 rounded shimmer");
    expect(html).toContain("h-48 rounded-md shimmer");
  });
});

describe("PageStateMessage", () => {
  it("renders title, description, and action", () => {
    const html = renderToStaticMarkup(
      <PageStateMessage
        title="ERR: データの取得に失敗しました"
        description="再読み込みしてください"
        actionLabel="再試行 →"
        onAction={() => {}}
      />,
    );

    expect(html).toContain("ERR: データの取得に失敗しました");
    expect(html).toContain("再読み込みしてください");
    expect(html).toContain("再試行 →");
  });
});
