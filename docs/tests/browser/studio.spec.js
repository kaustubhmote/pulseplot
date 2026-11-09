import { test, expect } from "@playwright/test";
import { readFile } from "node:fs/promises";

const baseline = JSON.parse(await readFile(new URL("../fixtures/python.json", import.meta.url), "utf8"));
const pages = {
  "source modules": "/",
  "generated document": "/index.html",
  "offline document": new URL("../../index.html", import.meta.url).href
};

for (const [name, url] of Object.entries(pages)) {
  test.describe(name, () => {
    let errors;
    test.beforeEach(async ({ page }) => {
      errors = [];
      page.on("pageerror", error => errors.push(error.message));
      page.on("dialog", dialog => dialog.accept());
      await page.goto(url);
      await expect(page.locator("#channelList input")).toHaveCount(2);
    });
    test.afterEach(() => expect(errors).toEqual([]));

    test("all templates render and preserve their original Python output", async ({ page }) => {
      for (const [template, python] of Object.entries(baseline)) {
        await page.selectOption("#templateSelect", template);
        await page.click("#loadTemplateBtn");
        await expect.poll(() => page.locator("#codeOutput").textContent()).toBe(python);
        await expect(page.locator("[data-element-id]").first()).toBeVisible();
      }
    });

    test("editing, history, project round trips, and image exports work", async ({ page }) => {
      const elements = page.locator("[data-element-id]");
      await page.click('[data-kind="pulse"]');
      await expect(elements).toHaveCount(1);
      await page.click("#undoBtn");
      await expect(elements).toHaveCount(0);
      await page.click("#redoBtn");
      await expect(elements).toHaveCount(1);
      await page.fill("#plotTitle", "Browser regression");
      await page.locator("#plotTitle").blur();
      await expect(page.locator("#codeOutput")).toContainText("Browser regression");
      await page.click("#themeBtn");
      await expect(page.locator("html")).toHaveAttribute("data-theme", "dark");

      const download = async selector => {
        const pending = page.waitForEvent("download");
        await page.click(selector);
        return readFile(await (await pending).path());
      };
      const project = JSON.parse((await download("#exportJsonBtn")).toString());
      expect(project.settings.title).toBe("Browser regression");
      expect(project.elements).toHaveLength(1);
      expect((await download("#downloadCodeBtn")).toString()).toContain("import pulseplot as pplot");
      expect((await download("#exportSvgBtn")).toString()).toContain("<svg");
      expect((await download("#exportPngBtn")).subarray(1, 4).toString()).toBe("PNG");

      await expect(page.locator("#saveStatus")).toHaveText("Saved locally");
      await page.reload();
      await expect(elements).toHaveCount(1);
      await expect(page.locator("#plotTitle")).toHaveValue("Browser regression");
      await page.click("#clearBtn");
      await expect(elements).toHaveCount(0);
      await page.setInputFiles("#projectFile", {
        name: "project.json", mimeType: "application/json", buffer: Buffer.from(JSON.stringify(project))
      });
      await expect(elements).toHaveCount(1);
      await expect(page.locator("#toast")).toHaveText("Project imported");
      await page.setViewportSize({ width: 390, height: 844 });
      await expect(page.locator('[data-kind="pulse"]')).toBeVisible();
      await expect(page.locator("#sequenceCanvas")).toBeVisible();
    });

    test("multi-selection applies batch edits and undoes them together", async ({ page }) => {
      await page.click('[data-kind="pulse"]');
      await page.click('[data-kind="pulse"]');
      const elements = page.locator("[data-element-id]");
      await expect(elements).toHaveCount(2);
      await elements.first().click({ modifiers: ["Control"] });
      await expect(page.locator("#inspector")).toContainText("2 selected");
      const phase = page.locator('[data-batch-prop="phase"]');
      await phase.fill("x");
      await phase.blur();
      await expect.poll(async () => (await page.locator("#codeOutput").textContent()).match(/ph=x/g)?.length).toBe(2);
      await page.click("#undoBtn");
      await expect(page.locator("#codeOutput")).not.toContainText("ph=x");
    });
  });
}
