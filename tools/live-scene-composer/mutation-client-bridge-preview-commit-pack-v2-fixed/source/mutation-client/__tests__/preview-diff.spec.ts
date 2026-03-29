import { summarizePreviewDiff } from "../preview-diff";

describe("summarizePreviewDiff", () => {
  it("counts changed fields", () => {
    const diff = summarizePreviewDiff({
      baseline: { a: 1 },
      draft: { a: 1 },
      staged: { a: 2, b: 3 }
    });
    expect(diff.changeCount).toBe(2);
  });
});
