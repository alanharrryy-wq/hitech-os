import HomePage from "../app/page";

describe("keystone home", () => {
  it("exports a home page component", () => {
    expect(typeof HomePage).toBe("function");
  });
});
