import asyncio
from curl_cffi.requests import AsyncSession

async def test_proxy(proxy_url: str):
    proxies = {"all": proxy_url}
    async with AsyncSession(impersonate="chrome124", proxies=proxies) as s:
        try:
            # Проверяем IP и страну
            res = await s.get("http://ip-api.com/json/", timeout=10.0)
            print("Данные прокси:", res.json())
        except Exception as e:
            print("Ошибка прокси:", e)

# Проверьте по очереди ttl-61, ttl-62, ttl-63
proxy = "http://5f1e9ba83a9e49398b249458b3bac67e-cc-RU-ttl-62:bfdd58168fda217f9b2502c8886a57c6@proxy.sousmarketfranchize.shop:80"
asyncio.run(test_proxy(proxy))