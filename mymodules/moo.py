from .. import loader, utils
from telethon import events
import asyncio

# meta developer: @unnv_4k

@loader.tds
class MsgMoo(loader.Module):
    """Отправка запросов боту moolokobot"""
    strings = {"name": "MsgMoo"}

    def __init__(self):
        self.bot_chat_id = 1606812809  # moolokobot
        self.processed = set()

    async def moocmd(self, message):
        """Отправить запрос боту moolokobot. Использование: .moo <текст>"""
        args = utils.get_args_raw(message)
        if not args:
            await utils.answer(message, "❌ Укажи текст запроса\nПример: .moo w")
            return

        # Отправляем запрос боту
        sent_msg = await self._client.send_message(self.bot_chat_id, args)
        await utils.answer(message, f"✅ Отправлено: <code>{args}</code>")

        # Ждём ответ и получаем кнопки
        await asyncio.sleep(2)

        async for msg in self._client.iter_messages(self.bot_chat_id, limit=3, from_user=self.bot_chat_id):
            if msg.id > sent_msg.id and msg.buttons:
                # Пересылаем сообщение с кнопками пользователю
                await msg.forward_to(message.chat_id)
                # Сохраняем ID сообщения для обработки callback
                self.processed.add(msg.id)
                break

    async def _button_handler(self, event):
        """Обработчик нажатий на кнопки"""
        if not hasattr(event, "data") or not event.data:
            return

        # Получаем данные кнопки
        btn_data = event.data.decode() if isinstance(event.data, bytes) else event.data

        # Отправляем данные кнопки боту
        await self._client.send_message(self.bot_chat_id, btn_data)
        await asyncio.sleep(1.5)

        # Получаем ответ от бота
        async for msg in self._client.iter_messages(self.bot_chat_id, limit=3, from_user=self.bot_chat_id):
            if msg.id > int(btn_data.split()[-1]) if btn_data.split() else 0:
                if msg.buttons:
                    # Пересылаем новое сообщение с кнопками
                    await msg.forward_to(event.chat_id)
                break

    async def client_ready(self):
        # Регистрируем обработчик callback
        self._client.add_event_handler(self._button_handler, events.CallbackQuery)