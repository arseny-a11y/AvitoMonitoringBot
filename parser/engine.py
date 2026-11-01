import asyncio
from curl_cffi.requests import AsyncSession
from camoufox.async_api import AsyncCamoufox
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from parser.clear_url import clear_avito_url
from config.config import settings



class AvitoParser:
    def __init__(self, proxy: str | None = None, headless: bool = True):
        self.proxy = proxy
        self.headless = headless
        self.browser_manager = None
        self.browser = None

    def proxy_config(self) -> dict | None:
        if not self.proxy:
            return None
        
        parsed = urlparse(self.proxy)

        proxy_dict = {
            "server" : f"http://{parsed.hostname}:{parsed.port}",
            "username" : parsed.username,
            "password" : parsed.password
        }

        return proxy_dict
    
    async def start(self):
        self.browser_manager = AsyncCamoufox(
            headless=self.headless,
            geoip=True,
            proxy=self.proxy_config(),
            os="windows",
            locale="ru-RU"
        )

        self.browser = await self.browser_manager.__aenter__()

    async def close(self):
        if self.browser_manager:
            await self.browser_manager.__aexit__(None, None, None)
            self.browser_manager = None
            self.browser = None

    async def get_page_html(self, url: str) -> str | None:
        if not self.browser:
            await self.start()

        page = await self.browser.new_page()

        try:
            async def block_heavy_resources(route):
                if route.request.resource_type in ["image","media","font"]:
                    await route.abort()
                    return

                url = route.request.url.lower()
                heavy_domains = ["mc.yandex.ru", "google-analytics.com", "yandex.ru/clck", "top-fwz1.mail.ru"]

                if any(domain in url for domain in heavy_domains):
                    await route.abort()
                    return
                
                await route.continue_()
                
            await page.route("**/*", block_heavy_resources)

            await page.goto(url, wait_until="domcontentloaded", timeout=60000)

            try:
                await page.wait_for_selector('div[data-marker="item"]')
            except Exception:
                await page.wait_for_timeout(2000)

            title = await page.title()
            print(f"Успешное подлючение, заголовок страницы: {title}")

            content = await page.content()

            return content
        
        except Exception as e:
            print(f"Ошибка загрузки страницы: {e}")
            return None
        
        finally:
            await page.close()

    def parse_items(self, html: str | None):
        soup = BeautifulSoup(html, "html.parser")

        cards = soup.find_all("div", attrs={"data-marker" : "item"})

        print(f"Найдено карточек : {len(cards)}")

async def main():

    proxy_url = settings.PROXY_ROTATION
    avito_url = "https://www.avito.ru/izhevsk/odezhda_obuv_aksessuary?q=джинсы"

    parser = AvitoParser(proxy=proxy_url, headless=False)

    try:
        html = await parser.get_page_html(avito_url)
        if html:
            print("html получен")
            print(html)
    finally:
        await parser.close()
if __name__ == "__main__":
    asyncio.run(main())