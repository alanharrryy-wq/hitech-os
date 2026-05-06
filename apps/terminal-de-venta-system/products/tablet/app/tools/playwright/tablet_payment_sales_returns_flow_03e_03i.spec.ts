import { test, expect } from "@playwright/test";

test.describe("PRISMA Tablet 03E-03I payment, sales and returns", () => {
  test("/pos keeps Cobro inside Vender", async ({ page }) => {
    await page.goto("/pos");
    await expect(page.getByRole("heading", { name: /Vender/i })).toBeVisible();
    await expect(page.getByText(/Cobro dentro de Vender/i)).toBeHidden();
  });

  test("sales aliases redirect to Ventas de hoy", async ({ page }) => {
    await page.goto("/sales");
    await expect(page).toHaveURL(/\/sales\/today/);
    await expect(page.getByText(/Ventas de hoy/i)).toBeVisible();
  });

  test("returns alias redirects to ticket list", async ({ page }) => {
    await page.goto("/returns");
    await expect(page).toHaveURL(/\/sales\/today/);
  });

  test("checkout alias redirects to POS", async ({ page }) => {
    await page.goto("/checkout");
    await expect(page).toHaveURL(/\/pos/);
  });
});
