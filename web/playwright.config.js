import { defineConfig } from '@playwright/test';
export default defineConfig({
  testDir: './tests', testMatch: 'browser.spec.js', workers: 1, timeout: 30000,
  outputDir: './test-results', reporter: [['list']],
  use: { baseURL: process.env.COULDHAPPEN_TEST_URL, browserName: 'chromium', trace: 'retain-on-failure' }
});
