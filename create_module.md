# 🔌 Создание модулей для Herikku Userbot

Юзербот Herikku имеет мощную модульную архитектуру. Вы можете легко расширять функционал бота, создавая собственные модули в папке `modules/` (пользовательские) или `modules/builtin/` (встроенные).

---

## 🛠️ Базовая структура модуля

Каждый модуль представляет собой класс Python, наследуемый от базового класса `Module` из `core.base_module`. 

Минимальный жизнеспособный шаблон модуля `modules/my_module.py`:

```python
from core.base_module import Module

class MyModule(Module):
    # --- Метаданные модуля ---
    NAME = 'MyModule'                              # Имя модуля (выводится в меню)
    AUTHOR = 'Ваш Никнейм'                         # Автор
    DESCRIPTION = 'Простой тестовый модуль'        # Описание модуля
    DEPENDENCIES = []                              # Список pip-зависимостей (авто-установка)
    COMMANDS = {                                   # Список команд для справки .help
        'hello': 'Отправить приветственное сообщение'
    }
    CONFIG_ICON = '🎈'                              # Иконка модуля в меню .config

    async def init(self, client, command_prefix, events, load_module,
        loaded_modules, config, config_path, install_package, bot_start_time):
        
        self.client = client
        self.prefix = command_prefix

        # Обработчик команды
        async def hello_handler(event):
            # Проверяем, что сообщение начинается с нашей команды
            if not event.text or not event.text.startswith(f'{self.prefix}hello'):
                return
                
            # Редактируем сообщение пользователя
            await event.edit("<b>🎈 Привет из нового модуля Herikku!</b>")

        # Регистрация обработчика на исходящие сообщения
        client.add_event_handler(hello_handler, events.NewMessage(outgoing=True))
```

---

## 🔬 Анатомия аргументов метода `init()`

Метод `init` — главная точка входа. При запуске бота загрузчик передает в него следующие аргументы:

| Аргумент | Тип | Описание |
| :--- | :--- | :--- |
| `client` | `TelegramClient` | Основной клиент Telethon (Ваш аккаунт). Используется для отправки СМС, работы с API. |
| `command_prefix` | `str` | Префикс команд юзербота (например, `.`). |
| `events` | `module` | Модуль `telethon.events` для подписки на события (`NewMessage`, `ChatAction` и т.д.). |
| `load_module` | `callable` | Функция для динамической подгрузки другого модуля по его файловому пути. |
| `loaded_modules` | `dict` | Словарь всех загруженных модулей текущего аккаунта `{name: instance}`. |
| `config` | `ConfigParser` | Парсер конфигурационного INI-файла текущего аккаунта. |
| `config_path` | `str` | Абсолютный путь к INI-файлу аккаунта (`config_account_{id}.ini`). |
| `install_package` | `callable` | Функция для тихой установки pip-пакетов во время работы. |
| `bot_start_time` | `datetime` | Точная временная метка старта юзербота (для расчета аптайма). |

---

## 📦 Автоматическое управление зависимостями (`DEPENDENCIES`)

Herikku умеет самостоятельно контролировать наличие библиотек. Если вашему модулю нужен сторонний пакет (например, `requests` или `beautifulsoup4`):
1. Просто укажите его имя в списке `DEPENDENCIES = ['requests']`.
2. При запуске загрузчик попытается сделать `import requests`. 
3. Если пакета нет, бот **автоматически** выполнит скрытую установку `pip install requests` перед инициализацией модуля.

---

## 💾 Работа с файлом конфигурации (INI)

Herikku выделяет под каждый аккаунт свой файл настроек. Рекомендуется сохранять настройки вашего модуля в отдельную секцию в этот файл.

Пример сохранения настроек при инициализации:
```python
import configparser

class ConfiguredModule(Module):
    NAME = 'MyConfig'
    # ...

    async def init(self, client, command_prefix, events, load_module,
        loaded_modules, config, config_path, install_package, bot_start_time):
        
        self.config = config
        self.config_path = config_path

        # Создаем секцию, если её нет
        if not config.has_section('MyConfig'):
            config.add_section('MyConfig')
            config.set('MyConfig', 'status', 'active')
            config.set('MyConfig', 'limit', '10')
            self._save_config() # Метод сохранения на диск

    def _save_config(self):
        with open(self.config_path, 'w', encoding='utf-8') as f:
            self.config.write(f)
```

---

## 🎨 Создание интерактивного Inline-меню (`CONFIG_HANDLER`)

Если вы хотите, чтобы ваш модуль можно было настраивать через кнопки панели управления по команде `.config`, вам нужно реализовать статический асинхронный метод `CONFIG_HANDLER`.

```python
    @staticmethod
    async def CONFIG_HANDLER(event, config, Button):
        # Обязательно декодируем callback_data
        data = event.data.decode('utf-8')
        
        # Проверяем, что клик предназначен нашему модулю (формат: module_имяфайла)
        if data == 'module_my_module_filename':
            status = config.get('MyConfig', 'status', fallback='disabled')
            
            text = "<b>⚙️ Настройки MyModule</b>\n\n"
            text += f"Статус: <code>{status}</code>"
            
            # Строим кнопки
            buttons = [
                [
                    Button.inline("🟢 Включить", b'my_mod_enable'),
                    Button.inline("❌ Выключить", b'my_mod_disable')
                ],
                [Button.inline("◀️ К модулям", b'settings_modules')]
            ]
            await event.edit(text, buttons=buttons)
            
        # Ловим клики по кнопкам
        elif data == 'my_mod_enable':
            config.set('MyConfig', 'status', 'active')
            # Не забываем сохранять конфиг (в реальном модуле потребуется записать файл)
            await event.answer("✅ Включено!", alert=True)
            # Перерисовываем меню
            await ConfiguredModule.CONFIG_HANDLER(event, config, Button)
```

---

## 🤖 Регистрация Inline-обработчиков (`INLINE_HANDLERS`)

Если ваш модуль должен расширять возможности встроенного (inline) бота (например, реагировать на инлайн-запросы `@ваш_бот help` или клики по кнопкам в чате), объявите метод `INLINE_HANDLERS`:

```python
    @staticmethod
    async def INLINE_HANDLERS(bot_client, events, config, loaded_modules):
        
        @bot_client.on(events.InlineQuery)
        async def custom_query_handler(event):
            query = event.text.strip().lower()
            if query != 'my_custom_query':
                return
                
            builder = event.builder
            # Создаем инлайн-карточку
            result = builder.article(
                title="🎈 Кастомный результат",
                text="Этот текст отправится при выборе карточки!"
            )
            await event.answer([result])
```

---

## 💡 Полезные советы разработчику

1. **Используйте HTML-разметку**: В Herikku клиентам принудительно установлен `parse_mode = html`. При отправке форматированного текста оборачивайте Markdown-символы функцией `from core.formatting import markdown_to_html` перед вызовом `.edit()` или используйте стандартный HTML (`<b>`, `<i>`, `<code>`, `<pre>`).
2. **Безопасность (`delete`)**: Если вы хотите заменить команду вызовом inline-карточки, не забывайте удалять сообщение-команду с помощью `await event.delete()`, чтобы очистить чат.
3. **Режимы чатов**: Всегда проверяйте контекст события. Если команда предназначена для администрирования групп, проверяйте `if event.is_private: return`.
