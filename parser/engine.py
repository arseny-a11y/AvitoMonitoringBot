import asyncio
from curl_cffi.requests import AsyncSession
from bs4 import BeautifulSoup
from parser.clear_url import clear_avito_url


class AvitoParser:
    def __init__(self, proxy: str | None = None):
        self.proxy = proxy
        self.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8",
            "Sec-Ch-Ua": '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "Referer": "https://www.avito.ru/",
        }

        #сессия пока пустая
        self.session: AsyncSession | None = None

    #метод инициализации сессии, позволяет отправлять запросы через одно TCP/TLS соединения , обходя антифрод и сохраняя файлы cookie
    async def init_session(self):
        if not self.session:
            proxies = {"all": self.proxy} if self.proxy else None
            self.session = AsyncSession(
                impersonate="chrome124",
                proxies=proxies,
                headers=self.headers,
                timeout=15.0
            )
    #метод для закрытия сессии
    async def close_session(self):
        if self.session:
            await self.session.close()
            self.session = None

    async def get_items(self, url: str) -> str | None:
        if not self.session:
            await self.init_session()
        
        clean_url = clear_avito_url(url)

        try:
            home_page = await self.session.get("https://www.avito.ru/")
            if home_page.status_code != 200:
                print(f"Главная страница отдала статус: {home_page.status_code}")

            await asyncio.sleep(2)

            response = await self.session.get(clean_url)

            if response.status_code != 200:
                print(f"Ошибка запроса: статус {response.status_code}")
                print("Что внутри ответа:\n", response.text[:400])
                return None
                
            return response.text
            
        except Exception as e:
            print(f"Сетевой сбой при парсинге: {e}")
            return None
        
    def parse_items(self, html: str | None):
        soup = BeautifulSoup(html, "html.parser")

        cards = soup.find_all("div", attrs={"data-marker" : "item"})

        print(f"Найдено карточек : {len(cards)}")

async def main():
    parser = AvitoParser("http://5f1e9ba83a9e49398b249458b3bac67e-cc-RU-ttl-64:bfdd58168fda217f9b2502c8886a57c6@proxy.sousmarketfranchize.shop:80")
    try:
        html = await parser.get_items("https://www.avito.ru/izhevsk/telefony/mobilnye_telefony/apple-ASgBAgICAkS0wA3OqzmwwQ2I_Dc?cd=1")

        if html:
            parser.parse_items(html)
    finally:
        await parser.close_session()

if __name__ == "__main__":
    asyncio.run(main())