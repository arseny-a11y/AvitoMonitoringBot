from curl_cffi.requests import AsyncSession
from camoufox.async_api import AsyncCamoufox
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from parser.clear_url import clear_avito_url
from config.config import settings
import unicodedata
import asyncio
import re




class AvitoParser:
    #инициализируем proxy и режим работы браузера "headless" (с открытием граф. окна или без)
    def __init__(self, proxy: str | None = None, headless: bool = True):
        self.proxy = proxy
        self.headless = headless
        self.browser_manager = None
        self.browser = None

    #метод формирования proxy, который принимает camoufox
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
    
    #метод инициализации сессии браузера
    async def start(self):
        self.browser_manager = AsyncCamoufox(
            headless=self.headless,
            geoip=True,
            proxy=self.proxy_config(),
            os="windows",
            locale="ru-RU"
        )

        self.browser = await self.browser_manager.__aenter__()

    #метод закрытия и отчистки контекстов браузера
    async def close(self):
        if self.browser_manager:
            await self.browser_manager.__aexit__(None, None, None)
            self.browser_manager = None
            self.browser = None

    #метод для получения html страницы
    async def get_page_html(self, url: str) -> str | None:
        #если браузер закрыт, инициализируем его
        if not self.browser:
            await self.start()

        page = await self.browser.new_page()

        try:
            async def block_heavy_resources(route):
                #не даем загружать картинки, видео и тд, чтоб загрузка шла быстрее
                if route.request.resource_type in ["image","media","font"]:
                    await route.abort()
                    return

                url = route.request.url.lower()

                #не даем Avito анализировать сайты перечисленные в списке, для более быстрой загрузки
                heavy_domains = ["mc.yandex.ru", "google-analytics.com", "yandex.ru/clck", "top-fwz1.mail.ru"]

                if any(domain in url for domain in heavy_domains):
                    await route.abort()
                    return
                
                await route.continue_()
                
            await page.route("**/*", block_heavy_resources)

            await page.goto(url, wait_until="domcontentloaded", timeout=60000)

            try:
                #ожидаем появление карточки товара на странице, только тогда забираем html код
                await page.wait_for_selector('div[data-marker="item"]')
            except Exception:
                await page.wait_for_timeout(3000)

            title = await page.title()
            print(f"Успешное подлючение, заголовок страницы: {title}")

            content = await page.content()

            return content
        
        except Exception as e:
            print(f"Ошибка загрузки страницы: {e}")
            return None
        
        finally:
            #закрываем страницу, чтобы не случилось
            await page.close()

    #метод для отчистки текста
    @staticmethod
    def clean_text(text: str | None, max_length: int | None = None) -> str | None:
        if not text:
            return None
        
        normalized = unicodedata.normalize("NFKD",text)
        text_normalized = " ".join(normalized.split())

        #если текст будет больше заявленной длинны укорачиваем
        if max_length is None or len(text_normalized) <= max_length:
            return text_normalized
        
        modification_text = text_normalized[:max_length].rsplit(" ", 1)[0]

        return f"{modification_text}..."
    
    def parse_items(self, html: str | None):
        if not html:
            return []
        
        soup = BeautifulSoup(html, "html.parser")

        #находим все карточки товаров на странице
        cards = soup.find_all("div", attrs={"data-marker" : "item"})

        items = []
        for card in cards:

            #достаем название
            title_block = card.find("div",class_=re.compile("^titleStep"))
            raw_title = title_block.get_text(strip=True) if title_block else "Название отсутствует"
            title = self.clean_text(raw_title)

            #достаем цену товара
            price_meta = card.find("meta",attrs={"itemprop" : "price"})
            price = int(price_meta["content"]) if price_meta and price_meta.get("content") else None
  
            #достаем описание карточки
            desc_block = card.find("div", class_=re.compile("^bottomBlock"))
            raw_desc = desc_block.get_text(strip=True) if desc_block else "Описание отсутствует" 
            description = self.clean_text(raw_desc, 150)
            
            #достаем id товара
            item_id = card.get("data-item-id")

            #достаем ссылку на товар
            link_tag = card.find("a", attrs={"data-marker" : "item-title"})
            url = f"https://www.avito.ru{link_tag.get('href')}" if link_tag and link_tag.get("href") else None

            #укорачиваем ссылку на товар
            short_url = clear_avito_url(url) if url else None

            #формируем список словарей с данными
            items.append({
                "id" : item_id,
                "title" : title,
                "price" : price,
                "description" : description,
                "url" : short_url
            })

        #возращаем собранные данные
        return items
    
async def main():
    parser = AvitoParser(proxy=settings.PROXY_ROTATION, headless=False)
    await parser.get_page_html("https://www.avito.ru/izhevsk?q=кро")

if __name__ == "__main__":
    asyncio.run(main())