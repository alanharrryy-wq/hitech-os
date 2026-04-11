import { describe, expect, it } from "vitest";

import { getTranslator } from "@/lib/i18n/dictionary";

describe("payments i18n contract", () => {
  it("keeps bilingual ownership keys wired", () => {
    const tEs = getTranslator("es");
    const tEn = getTranslator("en");

    expect(tEs("payments.page.title")).not.toContain("[[missing:");
    expect(tEn("payments.page.title")).not.toContain("[[missing:");
  });
});
