from playwright.async_api import async_playwright

async def get_browser_context():
    pw = await async_playwright().start()

    browser = await pw.chromium.launch(headless=False)
    # browser = await pw.firefox.connect(
    #     "wss://production-sfo.browserless.io/firefox/playwright?token=S5rLVbFVGssQnv6056e18a116cef9d4e942d2e8ec7"
    # )
    context = await browser.new_context()
    page = await context.new_page()
    return page, browser, context
