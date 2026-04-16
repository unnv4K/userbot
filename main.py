import asyncio
import logging
import importlib
from pathlib import Path

from telethon import TelegramClient, events
from telethon.sessions import StringSession

# ===== ВСТАВЬ СВОИ ДАННЫЕ ЗДЕСЬ =====
API_ID = 23760984
API_HASH = "c2ff30dd97d5e852d593148c5c498d44"
SESSION_STRING = ""  # Оставь пустым при первом запуске
# =====================================

logging.basicConfig(level=logging.INFO)

if SESSION_STRING:
    client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
else:
    client = TelegramClient("user", API_ID, API_HASH)

modules = {}
loaded_modules = set()

class Module:
    def __init__(self, name, commands=None):
        self.name = name
        self.commands = commands or {}

async def load_module(module_name, folder="modulesss"):
    if module_name in loaded_modules:
        return
    try:
        module = importlib.import_module(f"{folder}.{module_name}")
        if hasattr(module, "register"):
            mod = module.register()
            modules[mod.name] = mod
            loaded_modules.add(module_name)
            print(f"✅ Загружен: {mod.name}")
    except Exception as e:
        print(f"❌ Ошибка {module_name}: {e}")

@client.on(events.NewMessage)
async def command_handler(event):
    if not event.is_private:
        return
    text = event.raw_text
    if not text.startswith("."):
        return
    cmd_parts = text[1:].split()
    cmd_name = cmd_parts[0].lower()
    args = cmd_parts[1:]
    for mod in modules.values():
        if cmd_name in mod.commands:
            await mod.commands[cmd_name](event, args)
            return

@client.on(events.NewMessage(pattern=r"\.help(?:\s+(.+))?"))
async def help_handler(event):
    args = event.pattern_match.group(1)
    if args:
        mod_name = args.lower()
        if mod_name in modules:
            mod = modules[mod_name]
            cmds = " | ".join(mod.commands.keys())
            await event.reply(f"📦 {mod.name}\nКоманды: {cmds}")
        else:
            await event.reply(f"❌ Модуль {mod_name} не найден")
    else:
        if modules:
            msg = "🪐 Модули:\n\n"
            for name, mod in modules.items():
                cmds = " | ".join(list(mod.commands.keys())[:5])
                msg += f"▪️ {name}: ( {cmds} )\n"
            await event.reply(msg)
        else:
            await event.reply("❌ Нет загруженных модулей")

async def main():
    # Загружаем предустановленные модули
    preset_dir = Path(__file__).parent / "modulesss"
    if preset_dir.exists():
        for py_file in preset_dir.glob("*.py"):
            await load_module(py_file.stem, folder="modulesss")
    
    # Загружаем твои личные модули
    personal_dir = Path(__file__).parent / "mymodules"
    if personal_dir.exists():
        for py_file in personal_dir.glob("*.py"):
            await load_module(py_file.stem, folder="mymodules")
    
    await client.start()
    print("🤖 Юзербот запущен!")
    print(f"📦 Модулей: {len(modules)}")
    
    # Если сессии нет — выводим её
    if not SESSION_STRING:
        print(f"\n✅ Скопируй эту строку и сохрани для следующего запуска:")
        print(f"SESSION_STRING={client.session.save()}\n")
    
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
