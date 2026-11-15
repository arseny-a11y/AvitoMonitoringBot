from parser.engine import parser
from database.queries import save_items 
from aiogram import Bot
from aiogram.enums import ParseMode
from database.queries import save_items
from parser.engine import AvitoParser
import asyncio



def format_text(item) -> str:
    price = item.price

    if price:
        normalized_price = f"{price:,}".replace(","," ")
    else:
        normalized_price = "Цена не указана"

    message_lines = [
        "🔔 <b>Новое объявление!</b>\n",
        f"📌 <b>{item.title}</b>",
        f"💰 <b>Цена:</b> {normalized_price}"
    ]

    if item.description and item.description != "Описание отсутствует":
        message_lines.append(f"📝 <i>{item.description}</i>")
    if item.url:
        message_lines.append(f"\n🔗 <a href='{item.url}'>Перейти к объявлению</a>")

    return "\n".join(message_lines)

async def products_monitoring(bot: Bot, chat_id: int, url: str, interval: int):
    parser = AvitoParser()
    await parser.start()

    is_firts_run = True

    try:
        while True:
            try:
                html = await parser.get_page_html(url)
                items = parser.parse_items(html)

                #сохраняем список только новых позиций
                new_items = await save_items(items)

                if is_firts_run:
                    if new_items:
                        print(f"[Init] База инициализирована: сохранено {len(new_items)}")
                    is_firts_run = False

                elif new_items:
                    print(f"[Monitor] Обнаружено новых объявлений: {len(new_items)}")

                    for item in new_items:
                        text = format_text(item)
                        await bot.send_message(
                                chat_id=chat_id,
                                text=text,
                                parse_mode=ParseMode.HTML,
                                disable_web_page_preview=False #Форматироет красивое превью сайта, на которую введет ссылка
                            )
                        await asyncio.sleep(0.5)

            except Exception as e:
                print(f"[Monitor Error]: {e}")

            await asyncio.sleep(interval)

    except asyncio.CancelledError:
        print("[Monitor] Задача мониторинга принудительно остановлена.")
        raise

    finally:
        await parser.close()

class MonitoringManager:
    def __init__(self):
        self.current_url: str | None = None
        self.interval: int = 300
        self._task: asyncio.Task | None = None

    @property
    def is_running(self) -> bool:
        return self._task is not None and not self._task.done()
    
    def set_url(self, url: str) -> None:
        self.current_url = url.strip()

    def set_interval(self, number: int) -> None:
        self.interval = number

    def start(self, bot: Bot, chat_id: int, interval: int = 30) -> tuple[bool, str]:
        if self.is_running:
            return False, "Мониторинг уже запущен!"
        if not self.current_url:
            return False, "Сначала задайте ссылку для мониторинга"

        self._task = asyncio.create_task(
            products_monitoring(
                bot=bot,
                chat_id=chat_id,
                url=self.current_url,
                interval=self.interval
            )
        )
        return True, "Мониторинг успешно запущен!"

    def stop(self) -> tuple[bool, str]:
        if not self.is_running:
            return False, "Мониторинг не активен"

        self._task.cancel()
        self._task = None
        return True, "Мониторинг остановлен"

monitor_manager = MonitoringManager()