from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)  # 启动浏览器（有头模式）
    page = browser.new_page()
    page.goto("https://www.kuangweihua.com")
    page.screenshot(path="C:\\Github\\aigc-AdGraph\\part3_browser_use\\example.png")
    browser.close()
