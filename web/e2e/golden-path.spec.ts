import { expect, test } from "@playwright/test";

/**
 * One end-to-end path through the platform: a queue rendered from the case
 * type's own declaration, a case opened from it, a workflow transition
 * applied, and the resulting audit entry rendered back.
 */
test("an analyst claims a new alert and the audit trail records it", async ({
  page,
}) => {
  await page.goto("/aml?preset=unassigned&status=new");

  const row = page.getByRole("row").filter({ hasText: /AML-\d+/ }).first();
  const reference = (await row.getByText(/AML-\d+/).innerText()).trim();
  // The row navigates from a client handler, so retry until hydration lands.
  await expect(async () => {
    await row.click();
    await expect(page).toHaveURL(/\/aml\/case_/, { timeout: 2_000 });
  }).toPass({ timeout: 30_000 });

  await expect(page.getByText(reference).first()).toBeVisible();

  await page.getByRole("button", { name: "Claim & start review" }).click();

  await expect(
    page.getByRole("button", { name: "Claim & start review" }),
  ).toBeHidden();
  await expect(
    page.getByText('applied "Claim & start review"').first(),
  ).toBeVisible();
  await expect(page.getByText("In review").first()).toBeVisible();
});
