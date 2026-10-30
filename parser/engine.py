import asyncio
from curl_cffi.requests import AsyncSession
from bs4 import BeautifulSoup
from parser.clear_url import clear_avito_url


class AvitoParser:
    def __init__(self, proxy: str | None = None):
        self.proxy = {"all": proxy} if proxy else None
        self.headers = {
            "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/152.0.0.0 YaBrowser/26.10.0.0 Safari/537.36",
            "Accept" : "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language" : "ru,en;q=0.9,ko;q=0.8",
            "Referer" : "https://www.avito.ru/"
        }

    async def get_items(self, url: str):
        async with AsyncSession() as session:
            try:
                response = await session.get(
                    url,
                    headers=self.headers,
                    impersonate="chrome152",
                    proxies=self.proxy,
                    timeout=15.0
                )

                if response.status_code != 200:
                    print(f"Ошибка запроса: статус {response.status_code}")

                    return []
                return response.text[:200]
            except Exception as e:
                print(f"Сетевой сбой при парсинге: {e}")
                return []

# 
# parse = AvitoParser()
# parse.get_items(clean_url)

async def main():
    clean_url = clear_avito_url("https://www.avito.ru/izhevsk/odezhda_obuv_aksessuary/muzhskaya_odezhda/dzhinsy-ASgBAgICAkTeAtgL4ALgCw?cd=1&f=ASgBAgICA0TeAtgL4ALgC5aZGAI&q=джинсы")

    parser = AvitoParser()
    status = await parser.get_items(clean_url)
    print(status)

if __name__ == "__main__":
    asyncio.run(main())