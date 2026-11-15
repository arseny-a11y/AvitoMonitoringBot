from aiogram import Bot, Router
from aiogram.types import Message
from aiogram.filters import Command

from parser.monitoring import monitor_manager

monitor_router = Router()


@monitor_router.message(Command("start"))
async def cmd_start(message: Message):
    text = (
        
        "👋 <b>Avito Monitoring Bot</b>\n\n"

        "Бот автоматически отслеживает появление новых объявлений по заданной ссылке и мгновенно отправляет их в этот чат.\n\n"

        "📌 <b>Доступные команды:</b>\n"
        "• /set_url <code>[ссылка]</code> — задать поисковый URL Авито\n"
        "• /set_interval <code>[секунды]</code> — изменить частоту проверки (по умолч. 300 сек)\n"
        "• /start_monitor — запустить фоновый мониторинг\n"
        "• /stop_monitor — остановить мониторинг\n"
        "• /status — проверить текущее состояние и настройки\n\n"

        "<i>Начните с установки ссылки командой /set_url.</i>"
    )

    await message.answer(text=text, parse_mode="HTML")

@monitor_router.message(Command("set_interval"))
async def cmd_interval(message: Message):
    elements = message.text.split(maxsplit=1)

    if len(elements) < 2:
        return await message.answer(
            "❌ <b>Ошибка в формате команды!</b>\n\n"
            "Отправьте команду вместе с положительным числом (интервал между мониторингом в сек.), например:\n"
            "<code>/set_interval 300</code>", parse_mode="HTML"
        )
    
    number = elements[1]

    try:
        interval = int(number.strip())
    except ValueError:
        return await message.answer(
            "❌ Ошибка: интервал должен быть целым числом!"
        )

    if interval < 60:
        return await message.answer(
            "❌ Минимальное время мониторинга 60 сек."
        )
    
    monitor_manager.set_interval(interval)

    await message.answer(
        f"✅ Интервал успешно изменен на <b>{interval}</b> сек.",
        parse_mode="HTML"
    )
@monitor_router.message(Command("set_url"))
async def cmd_set_url(message: Message, bot:  Bot):
    elements = message.text.split(maxsplit=1)

    if len(elements) < 2 or not elements[1].strip().startswith("http"):
        return await message.answer(
            "❌ <b>Ошибка в формате команды!</b>\n\n"
            "Отправьте команду вместе с полной ссылкой на выдачу Авито, например:\n"
            "<code>/set_url https://www.avito.ru/kazan/avtomobili</code>", parse_mode="HTML"
        )

    new_url = elements[1].strip()

    is_running = monitor_manager.is_running
    #проверяем работал ли мониторинг до смены ссылки
    if is_running:
        #если работал глушим задачу
        monitor_manager.stop()

    #сохраняем новую ссылку в менеджер
    monitor_manager.set_url(new_url)

    #перезапускаем мониторинг на новую ссылку, если уже был активен
    if is_running:
        monitor_manager.start(bot=bot, chat_id=message.chat.id)
        await message.answer(
            f"🔄 <b>Ссылка обновлена!</b>\n"
            f"Мониторинг автоматически перезапущен на новый адрес:\n"
            f"<code>{new_url}</code>",
            parse_mode="HTML",
            disable_web_page_preview=True
        )
    else:
        await message.answer(
            f"✅ <b>Ссылка успешно сохранена:</b>\n"
            f"<code>{new_url}</code>\n\n"
            f"Чтобы включить мониторинг, отправьте команду: /start_monitor",
            parse_mode="HTML",
            disable_web_page_preview=True
        )
@monitor_router.message(Command("start_monitor"))
async def cmd_start_monitor(message: Message, bot: Bot):
    status, text = monitor_manager.start(
        bot=bot,
        chat_id=message.chat.id,
    )
    await message.answer(text)

@monitor_router.message(Command("stop_monitor"))
async def cmd_stop_monitor(message: Message, bot: Bot):
    status, text = monitor_manager.stop()
    await message.answer(text)

@monitor_router.message(Command("status"))
async def cmd_status(message: Message):
    status = "🟢 Работает" if monitor_manager.is_running else "🔴 Остановлен"
    current_url = monitor_manager.current_url or "Не задана"

    text = (
        f"📊 <b>Статус мониторинга:</b> {status}\n\n"
        f"🔗 <b>Текущий URL:</b>\n<code>{current_url}</code>"
    )

    await message.answer(text, parse_mode="HTML", disable_web_page_preview=True)