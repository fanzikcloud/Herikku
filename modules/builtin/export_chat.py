from core.base_module import Module
from datetime import datetime
import html
import os


class ExportChatModule(Module):
    NAME = 'Export Chat'
    AUTHOR = 'Herikku'
    DESCRIPTION = 'Экспорт чата в красивый HTML файл'
    DEPENDENCIES = []
    COMMANDS = {'exporthtml': 'Экспортировать текущий чат в HTML',
        'exporthtml <лимит>': 'Экспортировать последние N сообщений'}

    async def init(self, client, command_prefix, events, load_module,
        loaded_modules, config, config_path, install_package, bot_start_time):
        self.client = client
        self.prefix = command_prefix

        async def export_handler(event):
            if not event.text or not event.text.startswith(
                f'{self.prefix}exporthtml'):
                return
            args = event.text[len(f'{self.prefix}exporthtml'):].strip()
            limit = None
            if args and args.isdigit():
                limit = int(args)
                if limit > 10000:
                    await event.edit(
                        '⚠️ <b>Максимальный лимит: 10000 сообщений</b>')
                    return
            await event.edit('📥 <b>Начинаю экспорт чата...</b>')
            try:
                chat = await event.get_chat()
                chat_title = getattr(chat, 'title', getattr(chat,
                    'first_name', 'Unknown Chat'))
                messages = []
                count = 0
                await event.edit(
                    f'📥 <b>Загружаю сообщения...</b>\n⏳ Загружено: {count}')
                async for message in client.iter_messages(event.chat_id,
                    limit=limit):
                    messages.append(message)
                    count += 1
                    if count % 100 == 0:
                        await event.edit(
                            f'📥 <b>Загружаю сообщения...</b>\n⏳ Загружено: {count}'
                            )
                messages.reverse()
                await event.edit(
                    f'🎨 <b>Генерирую HTML...</b>\n📊 Всего сообщений: {len(messages)}'
                    )
                html_content = self._generate_html(chat_title, messages)
                filename = (
                    f"chat_export_{chat.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
                    )
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                await event.edit(
                    f'📤 <b>Отправляю файл...</b>\n📊 Сообщений: {len(messages)}'
                    )
                await event.delete()
                await client.send_file(event.chat_id, filename, caption=
                    f"""📄 <b>Экспорт чата: {chat_title}</b>

📊 Сообщений: <code>{len(messages)}</code>
📅 Дата: <code>{datetime.now().strftime('%d.%m.%Y %H:%M')}</code>"""
                    )
                os.remove(filename)
            except Exception as e:
                await event.edit(
                    f'❌ <b>Ошибка экспорта:</b>\n<code>{str(e)}</code>')
        client.add_event_handler(export_handler, events.NewMessage(outgoing
            =True))

    def _generate_html(self, chat_title, messages):
        total_messages = len(messages)
        unique_users = len(set(m.sender_id for m in messages if m.sender_id))
        media_count = len([m for m in messages if m.media])
        text_messages = len([m for m in messages if m.text])
        photos = len([m for m in messages if m.photo])
        videos = len([m for m in messages if m.video])
        documents = len([m for m in messages if m.document])
        voice = len([m for m in messages if m.voice])
        first_date = messages[0].date.strftime('%d.%m.%Y %H:%M'
            ) if messages and messages[0].date else 'N/A'
        last_date = messages[-1].date.strftime('%d.%m.%Y %H:%M'
            ) if messages and messages[-1].date else 'N/A'
        html_template = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html.escape(chat_title)} - Экспорт чата</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0a0a0a;
            color: #e0e0e0;
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: #111;
        }}
        
        .header {{
            background: #151515;
            border-bottom: 1px solid #222;
            padding: 24px 32px;
        }}
        
        .header-content {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 16px;
        }}
        
        .header-title {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        
        .chat-icon {{
            width: 40px;
            height: 40px;
            background: #1a1a1a;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        
        .header h1 {{
            font-size: 24px;
            font-weight: 600;
            color: #fff;
        }}
        
        .export-badge {{
            background: #1a1a1a;
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 12px;
            color: #888;
            display: flex;
            align-items: center;
            gap: 6px;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            padding: 24px 32px;
            background: #151515;
            border-bottom: 1px solid #222;
        }}
        
        .stat-card {{
            background: #1a1a1a;
            padding: 16px;
            border-radius: 8px;
            border: 1px solid #222;
        }}
        
        .stat-header {{
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 8px;
            color: #888;
            font-size: 13px;
        }}
        
        .stat-icon {{
            width: 16px;
            height: 16px;
        }}
        
        .stat-value {{
            font-size: 28px;
            font-weight: 600;
            color: #fff;
        }}
        
        .stat-label {{
            font-size: 12px;
            color: #666;
            margin-top: 4px;
        }}
        
        .details-section {{
            padding: 16px 32px;
            background: #151515;
            border-bottom: 1px solid #222;
        }}
        
        .details-toggle {{
            background: none;
            border: none;
            color: #888;
            cursor: pointer;
            font-size: 13px;
            display: flex;
            align-items: center;
            gap: 6px;
            padding: 8px 0;
        }}
        
        .details-toggle:hover {{
            color: #fff;
        }}
        
        .details-content {{
            display: none;
            margin-top: 12px;
            padding: 16px;
            background: #1a1a1a;
            border-radius: 8px;
            border: 1px solid #222;
        }}
        
        .details-content.active {{
            display: block;
        }}
        
        .detail-row {{
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #222;
        }}
        
        .detail-row:last-child {{
            border-bottom: none;
        }}
        
        .detail-label {{
            color: #888;
            font-size: 13px;
        }}
        
        .detail-value {{
            color: #fff;
            font-size: 13px;
            font-weight: 500;
        }}
        
        .search-box {{
            padding: 16px 32px;
            background: #151515;
            border-bottom: 1px solid #222;
            position: sticky;
            top: 0;
            z-index: 100;
            backdrop-filter: blur(10px);
        }}
        
        .search-wrapper {{
            position: relative;
        }}
        
        .search-icon {{
            position: absolute;
            left: 12px;
            top: 50%;
            transform: translateY(-50%);
            width: 18px;
            height: 18px;
            color: #666;
        }}
        
        .search-input {{
            width: 100%;
            padding: 10px 12px 10px 40px;
            background: #1a1a1a;
            border: 1px solid #222;
            border-radius: 8px;
            color: #fff;
            font-size: 14px;
            transition: all 0.2s;
        }}
        
        .search-input:focus {{
            outline: none;
            border-color: #333;
            background: #1f1f1f;
        }}
        
        .search-input::placeholder {{
            color: #666;
        }}
        
        .messages {{
            padding: 24px 32px;
            max-height: 70vh;
            overflow-y: auto;
        }}
        
        .message {{
            margin-bottom: 16px;
            display: flex;
            gap: 12px;
        }}
        
        .avatar {{
            width: 36px;
            height: 36px;
            border-radius: 8px;
            background: #1a1a1a;
            border: 1px solid #222;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #888;
            font-weight: 600;
            font-size: 14px;
            flex-shrink: 0;
        }}
        
        .message-body {{
            flex: 1;
            min-width: 0;
        }}
        
        .message-header {{
            display: flex;
            align-items: baseline;
            gap: 8px;
            margin-bottom: 4px;
        }}
        
        .sender-name {{
            font-weight: 600;
            color: #fff;
            font-size: 14px;
        }}
        
        .message-time {{
            font-size: 12px;
            color: #666;
        }}
        
        .message-content {{
            background: #1a1a1a;
            padding: 10px 14px;
            border-radius: 8px;
            border: 1px solid #222;
            word-wrap: break-word;
        }}
        
        .message-text {{
            color: #e0e0e0;
            font-size: 14px;
            line-height: 1.5;
            white-space: pre-wrap;
        }}
        
        .message.outgoing {{
            flex-direction: row-reverse;
        }}
        
        .message.outgoing .message-body {{
            display: flex;
            flex-direction: column;
            align-items: flex-end;
        }}
        
        .message.outgoing .message-header {{
            flex-direction: row-reverse;
        }}
        
        .message.outgoing .message-content {{
            background: #1f1f1f;
            border-color: #2a2a2a;
        }}
        
        .media-indicator {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 6px 10px;
            background: #151515;
            border: 1px solid #222;
            border-radius: 6px;
            font-size: 12px;
            color: #888;
            margin-top: 6px;
        }}
        
        .media-icon {{
            width: 14px;
            height: 14px;
        }}
        
        .reply-to {{
            background: #151515;
            padding: 8px 10px;
            border-radius: 6px;
            margin-bottom: 6px;
            font-size: 12px;
            border-left: 2px solid #333;
            color: #888;
        }}
        
        .footer {{
            background: #151515;
            padding: 24px 32px;
            text-align: center;
            border-top: 1px solid #222;
        }}
        
        .footer-content {{
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            color: #666;
            font-size: 13px;
        }}
        
        .footer-logo {{
            width: 20px;
            height: 20px;
        }}
        
        ::-webkit-scrollbar {{
            width: 8px;
        }}
        
        ::-webkit-scrollbar-track {{
            background: #151515;
        }}
        
        ::-webkit-scrollbar-thumb {{
            background: #2a2a2a;
            border-radius: 4px;
        }}
        
        ::-webkit-scrollbar-thumb:hover {{
            background: #333;
        }}
        
        @media (max-width: 768px) {{
            .header, .stats-grid, .search-box, .messages, .footer, .details-section {{
                padding-left: 16px;
                padding-right: 16px;
            }}
            
            .stats-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="header-content">
                <div class="header-title">
                    <div class="chat-icon">
                        <svg class="stat-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
                        </svg>
                    </div>
                    <h1>{html.escape(chat_title)}</h1>
                </div>
                <div class="export-badge">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>
                        <polyline points="3.27 6.96 12 12.01 20.73 6.96"/>
                        <line x1="12" y1="22.08" x2="12" y2="12"/>
                    </svg>
                    Экспорт • {datetime.now().strftime('%d.%m.%Y %H:%M')}
                </div>
            </div>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-header">
                    <svg class="stat-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
                    </svg>
                    <span>Всего сообщений</span>
                </div>
                <div class="stat-value">{total_messages:,}</div>
                <div class="stat-label">Текстовых: {text_messages:,}</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-header">
                    <svg class="stat-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
                        <circle cx="9" cy="7" r="4"/>
                        <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
                        <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
                    </svg>
                    <span>Участников</span>
                </div>
                <div class="stat-value">{unique_users}</div>
                <div class="stat-label">Уникальных пользователей</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-header">
                    <svg class="stat-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                        <circle cx="8.5" cy="8.5" r="1.5"/>
                        <polyline points="21 15 16 10 5 21"/>
                    </svg>
                    <span>Медиа файлов</span>
                </div>
                <div class="stat-value">{media_count}</div>
                <div class="stat-label">Фото: {photos} • Видео: {videos}</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-header">
                    <svg class="stat-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <circle cx="12" cy="12" r="10"/>
                        <polyline points="12 6 12 12 16 14"/>
                    </svg>
                    <span>Период</span>
                </div>
                <div class="stat-value">{len(set(m.date.date() for m in messages if m.date))}</div>
                <div class="stat-label">Дней активности</div>
            </div>
        </div>
        
        <div class="details-section">
            <button class="details-toggle" onclick="toggleDetails()">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="6 9 12 15 18 9"/>
                </svg>
                Подробная информация
            </button>
            <div class="details-content" id="detailsContent">
                <div class="detail-row">
                    <span class="detail-label">Первое сообщение</span>
                    <span class="detail-value">{first_date}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Последнее сообщение</span>
                    <span class="detail-value">{last_date}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Фотографий</span>
                    <span class="detail-value">{photos}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Видео</span>
                    <span class="detail-value">{videos}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Документов</span>
                    <span class="detail-value">{documents}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Голосовых сообщений</span>
                    <span class="detail-value">{voice}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Среднее сообщений в день</span>
                    <span class="detail-value">{total_messages // max(len(set(m.date.date() for m in messages if m.date)), 1)}</span>
                </div>
            </div>
        </div>
        
        <div class="search-box">
            <div class="search-wrapper">
                <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="11" cy="11" r="8"/>
                    <path d="m21 21-4.35-4.35"/>
                </svg>
                <input type="text" class="search-input" id="searchInput" placeholder="Поиск по сообщениям...">
            </div>
        </div>
        
        <div class="messages" id="messagesContainer">
"""
        me_id = None
        for msg in messages:
            if msg.out:
                me_id = msg.sender_id
                break
        for msg in messages:
            html_template += self._format_message(msg, me_id)
        html_template += """
        </div>
        
        <div class="footer">
            <div class="footer-content">
                <svg class="footer-logo" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M12 2L2 7l10 5 10-5-10-5z"/>
                    <path d="M2 17l10 5 10-5"/>
                    <path d="M2 12l10 5 10-5"/>
                </svg>
                <span>Herikku Userbot • Экспорт чата в HTML</span>
            </div>
        </div>
    </div>
    
    <script>
        // Поиск по сообщениям
        const searchInput = document.getElementById('searchInput');
        const messages = document.querySelectorAll('.message');
        
        searchInput.addEventListener('input', function(e) {
            const searchTerm = e.target.value.toLowerCase();
            
            messages.forEach(message => {
                const text = message.textContent.toLowerCase();
                if (text.includes(searchTerm)) {
                    message.style.display = 'flex';
                } else {
                    message.style.display = 'none';
                }
            });
        });
        
        // Переключение деталей
        function toggleDetails() {
            const content = document.getElementById('detailsContent');
            content.classList.toggle('active');
        }
        
        // Плавная прокрутка к последнему сообщению при загрузке
        window.addEventListener('load', function() {
            const container = document.getElementById('messagesContainer');
            container.scrollTop = container.scrollHeight;
        });
    </script>
</body>
</html>
"""
        return html_template

    def _format_message(self, msg, me_id):
        sender_name = 'Unknown'
        if msg.sender:
            sender_name = getattr(msg.sender, 'first_name', 'Unknown')
            last_name = getattr(msg.sender, 'last_name', '')
            if last_name:
                sender_name += f' {last_name}'
        avatar_letter = sender_name[0].upper() if sender_name else '?'
        msg_time = msg.date.strftime('%H:%M') if msg.date else ''
        msg_date = msg.date.strftime('%d.%m.%Y') if msg.date else ''
        message_class = 'outgoing' if msg.out else 'incoming'
        message_text = html.escape(msg.text) if msg.text else ''
        media_html = ''
        if msg.media:
            media_type = type(msg.media).__name__
            if 'Photo' in media_type:
                media_html = """<div class="media-indicator">
                    <svg class="media-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                        <circle cx="8.5" cy="8.5" r="1.5"/>
                        <polyline points="21 15 16 10 5 21"/>
                    </svg>
                    Фото
                </div>"""
            elif 'Document' in media_type:
                media_html = """<div class="media-indicator">
                    <svg class="media-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"/>
                        <polyline points="13 2 13 9 20 9"/>
                    </svg>
                    Файл
                </div>"""
            elif 'Video' in media_type:
                media_html = """<div class="media-indicator">
                    <svg class="media-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <polygon points="23 7 16 12 23 17 23 7"/>
                        <rect x="1" y="5" width="15" height="14" rx="2" ry="2"/>
                    </svg>
                    Видео
                </div>"""
            elif 'Audio' in media_type or 'Voice' in media_type:
                media_html = """<div class="media-indicator">
                    <svg class="media-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M9 18V5l12-2v13"/>
                        <circle cx="6" cy="18" r="3"/>
                        <circle cx="18" cy="16" r="3"/>
                    </svg>
                    Аудио
                </div>"""
            elif 'Sticker' in media_type:
                media_html = """<div class="media-indicator">
                    <svg class="media-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <circle cx="12" cy="12" r="10"/>
                        <path d="M8 14s1.5 2 4 2 4-2 4-2"/>
                        <line x1="9" y1="9" x2="9.01" y2="9"/>
                        <line x1="15" y1="9" x2="15.01" y2="9"/>
                    </svg>
                    Стикер
                </div>"""
            elif 'Poll' in media_type:
                media_html = """<div class="media-indicator">
                    <svg class="media-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <line x1="18" y1="20" x2="18" y2="10"/>
                        <line x1="12" y1="20" x2="12" y2="4"/>
                        <line x1="6" y1="20" x2="6" y2="14"/>
                    </svg>
                    Опрос
                </div>"""
            else:
                media_html = """<div class="media-indicator">
                    <svg class="media-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"/>
                    </svg>
                    Медиа
                </div>"""
        reply_html = ''
        if msg.reply_to and msg.reply_to.reply_to_msg_id:
            reply_html = """<div class="reply-to">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="display: inline; vertical-align: middle; margin-right: 4px;">
                    <polyline points="9 14 4 9 9 4"/>
                    <path d="M20 20v-7a4 4 0 0 0-4-4H4"/>
                </svg>
                Ответ на сообщение
            </div>"""
        if not message_text and media_html:
            message_text = '<i style="color: #666;">Медиа-сообщение</i>'
        elif not message_text:
            message_text = '<i style="color: #666;">Пустое сообщение</i>'
        return f"""
            <div class="message {message_class}">
                <div class="avatar">{avatar_letter}</div>
                <div class="message-body">
                    <div class="message-header">
                        <span class="sender-name">{html.escape(sender_name)}</span>
                        <span class="message-time">{msg_date} {msg_time}</span>
                    </div>
                    <div class="message-content">
                        {reply_html}
                        <div class="message-text">{message_text}</div>
                        {media_html}
                    </div>
                </div>
            </div>
        """
