import logging
import asyncio
from playwright.async_api import async_playwright, Browser, Page, BrowserContext

logger = logging.getLogger(__name__)

class BrowserManager:
    """
    Manages the Playwright browser instance and contexts.
    Designed for safety: visibly opens browser, allows manual user interaction.
    """
    def __init__(self):
        self.playwright = None
        self.browser: Browser | None = None
        self.context: BrowserContext | None = None
        self._lock = asyncio.Lock()

    async def start_browser(self, headless: bool = False):
        """
        Starts a visible Chromium instance.
        """
        async with self._lock:
            if self.browser:
                return

            logger.info("Starting Playwright browser...")
            self.playwright = await async_playwright().start()
            
            # Launch standard Chrome/Chromium
            # channel="chrome" uses the installed Chrome browser if available, which mimics real user better
            self.browser = await self.playwright.chromium.launch(
                headless=headless,
                channel="chrome", 
                args=[
                    "--start-maximized",
                    "--disable-blink-features=AutomationControlled" # Helps evade basic bot detection
                ]
            )
            
            # Create a persistent context or standard context
            # We use a standard context here, but could use persistent to save cookies
            self.context = await self.browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            
            logger.info("Browser started successfully.")

    async def get_page(self) -> Page:
        """
        Returns a new page in the current context. Enforces browser is started.
        """
        if not self.browser or not self.context:
            await self.start_browser()
        
        page = await self.context.new_page()
        return page

    async def close(self):
        """
        Closes the browser and stops Playwright.
        """
        async with self._lock:
            if self.context:
                await self.context.close()
                self.context = None
            
            if self.browser:
                await self.browser.close()
                self.browser = None
            
            if self.playwright:
                await self.playwright.stop()
                self.playwright = None
            
            logger.info("Browser closed.")

    async def navigate_to_job(self, url: str) -> Page:
        """
        Navigates to a specific job URL and returns the page object.
        """
        page = await self.get_page()
        try:
            logger.info(f"Navigating to {url}")
            await page.goto(url, wait_until="domcontentloaded")
            return page
        except Exception as e:
            logger.error(f"Failed to navigate to {url}: {str(e)}")
            await page.close()
            raise

    async def prefill_form_fields(self, page: Page, user_data: dict):
        """
        Attempts to pre-fill common form fields on job application pages.
        This is best-effort and may not work on all sites.
        
        Args:
            page: The Playwright page object
            user_data: Dict with keys like 'name', 'email', 'phone'
        """
        try:
            # Common field selectors for name
            name_selectors = [
                'input[name*="name" i]',
                'input[placeholder*="name" i]',
                'input[id*="name" i]',
                '#firstName',
                '#fullName',
            ]
            
            email_selectors = [
                'input[type="email"]',
                'input[name*="email" i]',
                'input[placeholder*="email" i]',
            ]
            
            phone_selectors = [
                'input[type="tel"]',
                'input[name*="phone" i]',
                'input[name*="mobile" i]',
                'input[placeholder*="phone" i]',
            ]
            
            # Try to fill name
            if 'name' in user_data:
                for selector in name_selectors:
                    try:
                        elem = page.locator(selector).first
                        if await elem.is_visible():
                            await elem.fill(user_data['name'])
                            logger.info(f"Filled name field: {selector}")
                            break
                    except:
                        continue
            
            # Try to fill email
            if 'email' in user_data:
                for selector in email_selectors:
                    try:
                        elem = page.locator(selector).first
                        if await elem.is_visible():
                            await elem.fill(user_data['email'])
                            logger.info(f"Filled email field: {selector}")
                            break
                    except:
                        continue
            
            # Try to fill phone
            if 'phone' in user_data:
                for selector in phone_selectors:
                    try:
                        elem = page.locator(selector).first
                        if await elem.is_visible():
                            await elem.fill(user_data['phone'])
                            logger.info(f"Filled phone field: {selector}")
                            break
                    except:
                        continue
                        
        except Exception as e:
            logger.warning(f"Pre-fill encountered an error (non-fatal): {e}")

    async def attach_resume(self, page: Page, resume_path: str):
        """
        Attempts to attach a resume file to a file input on the page.
        
        Args:
            page: The Playwright page object
            resume_path: Absolute path to the resume PDF file
        """
        try:
            file_input_selectors = [
                'input[type="file"]',
                'input[accept=".pdf"]',
                'input[accept*="pdf" i]',
                'input[name*="resume" i]',
                'input[name*="cv" i]',
            ]
            
            for selector in file_input_selectors:
                try:
                    elem = page.locator(selector).first
                    if await elem.count() > 0:
                        await elem.set_input_files(resume_path)
                        logger.info(f"Attached resume using: {selector}")
                        return True
                except:
                    continue
            
            logger.warning("No file input found for resume attachment")
            return False
            
        except Exception as e:
            logger.error(f"Failed to attach resume: {e}")
            return False

# Global instance
browser_manager = BrowserManager()
