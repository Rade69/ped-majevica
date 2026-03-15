/**
 * E2E Tests for PED Majevica using Playwright
 * Run with: npx playwright test
 */

const { test, expect } = require("@playwright/test");

test.describe("PED Majevica Website", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/");
  });

  test.describe("Homepage", () => {
    test("should load the homepage", async ({ page }) => {
      await expect(page).toHaveTitle(/PED Majevica/i);
    });

    test("should display navigation menu", async ({ page }) => {
      await expect(page.locator("nav")).toBeVisible();
      await expect(page.locator('text="Početna"')).toBeVisible();
    });

    test("should display hero section", async ({ page }) => {
      await expect(page.locator(".hero, section.hero")).toBeVisible();
    });
  });

  test.describe("Gallery", () => {
    test("should navigate to gallery", async ({ page }) => {
      await page.click('text="Galerija"');
      await expect(page).toHaveURL(/.*galerija/);
    });

    test("should display gallery images", async ({ page }) => {
      await page.goto("/galerija.html");
      const images = page.locator(".gallery img, .gallery-item");
      await expect(images.first()).toBeVisible();
    });
  });

  test.describe("Membership Form", () => {
    test("should display membership form", async ({ page }) => {
      await page.click('text="Učlanite se"');
      await expect(page.locator("form")).toBeVisible();
    });

    test("should validate form fields", async ({ page }) => {
      await page.goto("/uclanite-se.html");
      await page.click('button[type="submit"]');
      // Check for validation errors
      const errors = page.locator(".error, .invalid");
      expect(await errors.count()).toBeGreaterThan(0);
    });
  });

  test.describe("Authentication", () => {
    test("should navigate to login page", async ({ page }) => {
      await page.click('text="Prijava"');
      await expect(page).toHaveURL(/.*login/);
    });

    test("should show error for invalid credentials", async ({ page }) => {
      await page.goto("/login.html");
      await page.fill('input[name="username"]', "invalid");
      await page.fill('input[name="password"]', "wrong");
      await page.click('button[type="submit"]');
      await expect(page.locator(".error, .alert")).toBeVisible();
    });
  });

  test.describe("Blog Posts", () => {
    test("should load blog posts from API", async ({ page }) => {
      const response = await page.request.get("/api/posts");
      expect(response.ok()).toBeTruthy();
      const data = await response.json();
      expect(data.success).toBe(true);
    });

    test("should display posts on homepage", async ({ page }) => {
      // Check if posts section exists
      const postsSection = page.locator(".posts, .blog-posts");
      if (await postsSection.count() > 0) {
        await expect(postsSection.first()).toBeVisible();
      }
    });
  });

  test.describe("Events", () => {
    test("should load events from API", async ({ page }) => {
      const response = await page.request.get("/api/events");
      expect(response.ok()).toBeTruthy();
    });
  });

  test.describe("Trails", () => {
    test("should load trails from API", async ({ page }) => {
      const response = await page.request.get("/api/trails");
      expect(response.ok()).toBeTruthy();
    });
  });

  test.describe("Responsive Design", () => {
    test("should work on mobile", async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 });
      await page.goto("/");
      await expect(page).toHaveTitle(/PED Majevica/i);
    });

    test("should work on tablet", async ({ page }) => {
      await page.setViewportSize({ width: 768, height: 1024 });
      await page.goto("/");
      await expect(page).toHaveTitle(/PED Majevica/i);
    });
  });

  test.describe("Accessibility", () => {
    test("should have proper heading structure", async ({ page }) => {
      const h1 = page.locator("h1");
      await expect(h1).toHaveCount(1);
    });

    test("should have alt text on images", async ({ page }) => {
      const images = page.locator("img");
      const count = await images.count();
      for (let i = 0; i < count; i++) {
        const alt = await images.nth(i).getAttribute("alt");
        // Skip decorative images
        const src = await images.nth(i).getAttribute("src");
        if (src && !src.includes("decorative") && !src.includes("icon")) {
          expect(alt).toBeTruthy();
        }
      }
    });
  });
});
