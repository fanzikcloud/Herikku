# 🤖 Herikku Userbot

<div align="center">

![Banner](core/assets/img/banner.png)

**Мощный и гибкий Telegram Userbot на Python**

[🇷🇺 Русский](#-русская-версия) | [🇬🇧 English](#-english-version)

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Telethon](https://img.shields.io/badge/Telethon-Latest-orange.svg)](https://github.com/LonamiWebs/Telethon)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

</div>

---

## 🇷🇺 Русская версия

### 📋 Описание

Herikku - это продвинутый Telegram Userbot с модульной архитектурой, поддержкой множественных аккаунтов и встроенным inline-ботом. Идеально подходит для автоматизации задач в Telegram.

### ✨ Основные возможности

- 🔌 **Модульная система** - легко добавляйте и удаляйте модули
- 👥 **Мультиаккаунт** - управление несколькими Telegram аккаунтами
- 🤖 **Inline бот** - встроенный бот с защитой от посторонних
- 🎨 **Система тем** - настраиваемые темы оформления
- 🔐 **Система прав** - гибкое управление доступом к командам
- 🌐 **Web авторизация** - удобная авторизация через браузер
- 💾 **Бэкапы** - создание и восстановление резервных копий
- 🔄 **Алиасы** - создавайте короткие команды для длинных
- 🛡️ **Антиспам** - защита от спама в чатах
- 📝 **Автоответчик** - автоматические ответы на сообщения

### 📦 Встроенные модули

#### Системные модули
- **backup** - создание и восстановление бэкапов
- **config_menu** - управление конфигурацией
- **help** - справка по командам
- **info** - информация о пользователе/чате
- **module_manager** - управление модулями
- **permissions_manager** - управление правами
- **ping** - проверка скорости отклика
- **prefix** - изменение префикса команд
- **system** - системные команды
- **terminal** - выполнение shell команд
- **theme_manager** - управление темами
- **alias** - система алиасов команд

#### Дополнительные модули
- **antispam** - защита от спама
- **autoreply** - автоответчик
- **export_chat** - экспорт истории чата
- **fastfetch** - системная информация
- **qrcode** - генерация QR кодов
- **rpmod** - ролевые игры
- **spam** - массовая отправка сообщений
- **time_in_nick** - время в имени профиля
- **typewriter** - эффект печатной машинки
- **voice_to_text** - распознавание голоса
- **watermark** - водяные знаки на изображениях
- **weather** - прогноз погоды

### 🚀 Установка

1. **Клонируйте репозиторий**
```bash
git clone https://github.com/fanzikcloud/Herikku.git
cd Herikku
```

2. **Установите зависимости**
```bash
pip install -r requirements.txt
```

3. **Запустите бота**
```bash
python main.py
```

4. **Следуйте инструкциям** для авторизации через web-интерфейс

### ⚙️ Конфигурация

При первом запуске создаются файлы конфигурации:
- `config.ini` - основные настройки
- `proxy.ini` - настройки прокси (опционально)
- `permissions.json` - права доступа
- `themes.json` - темы оформления
- `aliases.json` - алиасы команд

### 📝 Использование

Префикс по умолчанию: `.`

Примеры команд:
```
.help - список всех команд
.ping - проверка скорости
.info - информация о пользователе
.modules - список модулей
.alias add test .help - создать алиас
```

### 🔧 Добавление модулей

Создайте файл в папке `modules/` или `modules/builtin/`:

```python
from core.base_module import BaseModule

class MyModule(BaseModule):
    def __init__(self):
        super().__init__(
            name="mymodule",
            description="Описание модуля",
            version="1.0.0",
            author="Ваше имя"
        )
    
    async def init(self, client):
        @client.on_command("mycommand")
        async def my_command(event):
            await event.edit("Привет!")
```

### 🛡️ Безопасность

- Все конфигурационные файлы с приватными данными исключены из git
- Session файлы не попадают в репозиторий
- Inline бот защищен от посторонних пользователей
- Система прав доступа к командам

### 📄 Лицензия

Этот проект распространяется под лицензией MIT. Подробности в файле [LICENSE](LICENSE).

### 🤝 Вклад в проект

Pull requests приветствуются! Для крупных изменений сначала откройте issue для обсуждения.

### 📞 Поддержка

Если у вас возникли вопросы или проблемы, создайте [issue](https://github.com/fanzikcloud/Herikku/issues).

---

## 🇬🇧 English Version

### 📋 Description

Herikku is an advanced Telegram Userbot with modular architecture, multi-account support, and built-in inline bot. Perfect for automating tasks in Telegram.

### ✨ Key Features

- 🔌 **Modular System** - easily add and remove modules
- 👥 **Multi-Account** - manage multiple Telegram accounts
- 🤖 **Inline Bot** - built-in bot with protection from strangers
- 🎨 **Theme System** - customizable themes
- 🔐 **Permission System** - flexible command access control
- 🌐 **Web Authorization** - convenient browser-based auth
- 💾 **Backups** - create and restore backups
- 🔄 **Aliases** - create short commands for long ones
- 🛡️ **Anti-Spam** - chat spam protection
- 📝 **Auto-Reply** - automatic message responses

### 📦 Built-in Modules

#### System Modules
- **backup** - create and restore backups
- **config_menu** - configuration management
- **help** - command reference
- **info** - user/chat information
- **module_manager** - module management
- **permissions_manager** - permission management
- **ping** - response speed check
- **prefix** - change command prefix
- **system** - system commands
- **terminal** - execute shell commands
- **theme_manager** - theme management
- **alias** - command alias system

#### Additional Modules
- **antispam** - spam protection
- **autoreply** - auto-responder
- **export_chat** - export chat history
- **fastfetch** - system information
- **qrcode** - QR code generation
- **rpmod** - role-playing games
- **spam** - mass message sending
- **time_in_nick** - time in profile name
- **typewriter** - typewriter effect
- **voice_to_text** - voice recognition
- **watermark** - image watermarks
- **weather** - weather forecast

### 🚀 Installation

1. **Clone the repository**
```bash
git clone https://github.com/fanzikcloud/Herikku.git
cd Herikku
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run the bot**
```bash
python main.py
```

4. **Follow the instructions** for web-based authorization

### ⚙️ Configuration

Configuration files are created on first run:
- `config.ini` - main settings
- `proxy.ini` - proxy settings (optional)
- `permissions.json` - access permissions
- `themes.json` - themes
- `aliases.json` - command aliases

### 📝 Usage

Default prefix: `.`

Example commands:
```
.help - list all commands
.ping - check speed
.info - user information
.modules - list modules
.alias add test .help - create alias
```

### 🔧 Adding Modules

Create a file in `modules/` or `modules/builtin/`:

```python
from core.base_module import BaseModule

class MyModule(BaseModule):
    def __init__(self):
        super().__init__(
            name="mymodule",
            description="Module description",
            version="1.0.0",
            author="Your name"
        )
    
    async def init(self, client):
        @client.on_command("mycommand")
        async def my_command(event):
            await event.edit("Hello!")
```

### 🛡️ Security

- All configuration files with private data are excluded from git
- Session files are not included in the repository
- Inline bot is protected from unauthorized users
- Command access permission system

### 📄 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) file for details.

### 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss.

### 📞 Support

If you have questions or issues, create an [issue](https://github.com/fanzikcloud/Herikku/issues).

---

<div align="center">

**Made with ❤️ by [fanzikcloud](https://github.com/fanzikcloud)**

⭐ Star this repo if you find it useful!

</div>
