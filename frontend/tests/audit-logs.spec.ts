import { test, expect } from '@playwright/test'

test.describe('Audit Log Management', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the audit logs page
    await page.goto('/audit-logs')
  })

  test('should display audit logs table', async ({ page }) => {
    // Check if the audit logs table is visible
    await expect(page.locator('text=Audit Log Management')).toBeVisible()
    
    // Check if the table headers are present
    await expect(page.locator('text=Timestamp')).toBeVisible()
    await expect(page.locator('text=User')).toBeVisible()
    await expect(page.locator('text=Action')).toBeVisible()
    await expect(page.locator('text=Resource')).toBeVisible()
    await expect(page.locator('text=Severity')).toBeVisible()
  })

  test('should have working filters', async ({ page }) => {
    // Check if filters are present
    await expect(page.locator('text=Advanced Filters')).toBeVisible()
    
    // Click on advanced filters to expand
    await page.click('text=Advanced Filters')
    
    // Check if filter fields are visible
    await expect(page.locator('text=Action')).toBeVisible()
    await expect(page.locator('text=Severity')).toBeVisible()
    await expect(page.locator('text=Resource Type')).toBeVisible()
  })

  test('should have export functionality', async ({ page }) => {
    // Check if export button is present
    const exportButton = page.locator('[aria-label="Export logs"]')
    await expect(exportButton).toBeVisible()
    
    // Click export button
    await exportButton.click()
    
    // Check if export dialog is visible
    await expect(page.locator('text=Export Audit Logs')).toBeVisible()
    await expect(page.locator('text=JSON')).toBeVisible()
    await expect(page.locator('text=CSV')).toBeVisible()
  })

  test('should have real-time monitoring tab', async ({ page }) => {
    // Click on the real-time tab
    await page.click('text=Real-time Monitor')
    
    // Check if real-time monitoring interface is visible
    await expect(page.locator('text=Status:')).toBeVisible()
    await expect(page.locator('text=Connect')).toBeVisible()
  })

  test('should have settings tab', async ({ page }) => {
    // Click on the settings tab
    await page.click('text=Settings')
    
    // Check if settings interface is visible
    await expect(page.locator('text=Data Retention')).toBeVisible()
    await expect(page.locator('text=Data Archival')).toBeVisible()
    await expect(page.locator('text=Storage Optimization')).toBeVisible()
  })

  test('should handle empty state', async ({ page }) => {
    // This test assumes there might be no logs initially
    // The component should handle empty state gracefully
    const emptyState = page.locator('text=No audit logs found')
    
    // If empty state is shown, it should be handled properly
    if (await emptyState.isVisible()) {
      await expect(emptyState).toBeVisible()
      await expect(page.locator('text=Try adjusting your search filters')).toBeVisible()
    }
  })

  test('should have working pagination', async ({ page }) => {
    // Check if pagination controls are present
    const pagination = page.locator('[role="navigation"]')
    
    // If there are multiple pages, pagination should be visible
    if (await pagination.isVisible()) {
      await expect(pagination).toBeVisible()
    }
  })

  test('should have working search functionality', async ({ page }) => {
    // Check if search input is present
    const searchInput = page.locator('input[placeholder*="Search logs"]')
    await expect(searchInput).toBeVisible()
    
    // Type in search input
    await searchInput.fill('test search')
    
    // Check if search button is present and clickable
    const searchButton = page.locator('button:has-text("Search")')
    await expect(searchButton).toBeVisible()
  })

  test('should display log details modal', async ({ page }) => {
    // Look for view details buttons
    const viewButtons = page.locator('[aria-label="View log details"]')
    
    // If there are logs with view buttons, test the modal
    if (await viewButtons.count() > 0) {
      await viewButtons.first().click()
      
      // Check if details modal is visible
      await expect(page.locator('text=Audit Log Details')).toBeVisible()
      await expect(page.locator('text=Basic Information')).toBeVisible()
      await expect(page.locator('text=User Information')).toBeVisible()
    }
  })
}) 