from core.base_module import Module
import json
import random
from telethon import events, Button


class RockPaperScissorsModule(Module):
    NAME = 'RockPaperScissors'
    AUTHOR = 'Herikku'
    DESCRIPTION = 'Игра Камень, Ножницы, Бумага на двоих через inline-бота (.rps в ответ на СМС)'
    DEPENDENCIES = []
    COMMANDS = {
        'rps': 'Бросить вызов в Камень, Ножницы, Бумага (нужно ответить на СМС оппонента)'
    }
    CONFIG_ICON = '✂️'

    # Реестр запущенных игр в ОЗУ:
    # { game_key: { 'p1': id, 'p2': id, 'p1_name': str, 'p2_name': str, 'p1_choice': str, 'p2_choice': str, 'status': 'waiting/active/ended' } }
    GAMES = {}

    @staticmethod
    async def INLINE_HANDLERS(bot_client, events, config, loaded_modules):
        owner_id = None

        @bot_client.on(events.InlineQuery)
        async def rps_inline_query(event):
            nonlocal owner_id
            query = event.text.strip()
            if not query.startswith('rps_duel_'):
                return
                
            if owner_id is None:
                owner_id = event.sender_id
                
            if event.sender_id != owner_id:
                await event.answer([])
                return

            # Формат запроса: rps_duel_{opponent_id}_{timestamp}
            parts = query.split('_')
            if len(parts) < 4:
                return

            opponent_id = int(parts[2])
            builder = event.builder
            text = f"✂️ <b>Камень, Ножницы, Бумага!</b>\n\n" \
                   f"Вызов брошен пользователю с ID: <code>{opponent_id}</code>\n" \
                   f"<i>Нажмите на кнопку ниже, чтобы принять вызов!</i>"

            buttons = [[Button.inline("⚔️ Принять вызов", f"rps_accept_{opponent_id}_{owner_id}")]]
            result = builder.article(
                title="✂️ Камень, Ножницы, Бумага: Дуэль!",
                text=text,
                buttons=buttons
            )
            await event.answer([result], cache_time=0)

        # Обработчик нажатия на кнопки принятия дуэли и выбора предметов
        @bot_client.on(events.CallbackQuery(pattern=b'rps_'))
        async def rps_callback_handler(event):
            data = event.data.decode('utf-8')

            # 1. ПРИНЯТИЕ ДУЭЛИ ОППОНЕНТОМ
            if data.startswith('rps_accept_'):
                parts = data.split('_')
                opponent_id = int(parts[2])
                p1_id = int(parts[3]) # создатель (owner)
                p2_id = event.sender_id # оппонент

                if p2_id != opponent_id:
                    await event.answer("❌ Этот вызов брошен не вам!", alert=True)
                    return

                game_key = f"{event.chat_id}_{event.message_id}"
                
                # Инициализация игры
                TicTacToeModule = None
                RockPaperScissorsModule.GAMES[game_key] = {
                    'p1': p1_id,
                    'p2': p2_id,
                    'p1_name': (await bot_client.get_entity(p1_id)).first_name,
                    'p2_name': (await bot_client.get_entity(p2_id)).first_name,
                    'p1_choice': None,
                    'p2_choice': None,
                    'status': 'active'
                }

                await event.answer("🎮 Игра началась! Сделайте ваш выбор!", alert=True)
                await draw_game_state(event, game_key)

            # 2. ИГРОВОЙ ВЫБОР (Камень, Ножницы, Бумага)
            elif data.startswith('rps_choice_'):
                # Формат: rps_choice_{rock/paper/scissors}_{chat_id}_{message_id}
                parts = data.split('_')
                choice = parts[2]
                game_key = f"{parts[3]}_{parts[4]}"

                game = RockPaperScissorsModule.GAMES.get(game_key)
                if not game:
                    await event.answer("⚠️ Игра не найдена или уже завершена!", alert=True)
                    return

                if game['status'] != 'active':
                    await event.answer("🎮 Игра уже завершена!", alert=True)
                    return

                current_player = event.sender_id
                if current_player != game['p1'] and current_player != game['p2']:
                    await event.answer("❌ Вы не участвуете в этой дуэли!", alert=True)
                    return

                # Фиксируем выбор
                choices_map = {
                    'rock': '🪨 Камень',
                    'paper': '📄 Бумага',
                    'scissors': '✂️ Ножницы'
                }

                choice_readable = choices_map.get(choice)

                if current_player == game['p1']:
                    if game['p1_choice']:
                        await event.answer("⚠️ Вы уже сделали свой выбор!", alert=True)
                        return
                    game['p1_choice'] = choice
                else:
                    if game['p2_choice']:
                        await event.answer("⚠️ Вы уже сделали свой выбор!", alert=True)
                        return
                    game['p2_choice'] = choice

                await event.answer(f"🎉 Вы выбрали {choice_readable}! Ожидаем соперника...", alert=True)

                # Проверяем, сделали ли оба игрока выбор
                if game['p1_choice'] and game['p2_choice']:
                    game['status'] = 'ended'
                    
                await draw_game_state(event, game_key)

        # Отрисовка состояния игры
        async def draw_game_state(event, game_key):
            game = RockPaperScissorsModule.GAMES.get(game_key)
            if not game:
                return

            choices_visual = {
                'rock': '🪨',
                'paper': '📄',
                'scissors': '✂️'
            }

            p1_status = "✅ Выбор сделан" if game['p1_choice'] else "⏳ Выбирает..."
            p2_status = "✅ Выбор сделан" if game['p2_choice'] else "⏳ Выбирает..."

            if game['status'] == 'active':
                text = f"✂️ <b>Камень, Ножницы, Бумага — Игра началась!</b>\n" \
                       f"───────────────────────────────────\n" \
                       f"👤 <b>{game['p1_name']}:</b> {p1_status}\n" \
                       f"👤 <b>{game['p2_name']}:</b> {p2_status}\n\n" \
                       f"<i>Сделайте свой выбор кнопками ниже:</i>"

                buttons = [[
                    Button.inline("🪨 Камень", f"rps_choice_rock_{game_key}"),
                    Button.inline("✂️ Ножницы", f"rps_choice_scissors_{game_key}"),
                    Button.inline("📄 Бумага", f"rps_choice_paper_{game_key}")
                ]]
            else: # ended
                c1 = game['p1_choice']
                c2 = game['p2_choice']

                emoji1 = choices_visual[c1]
                emoji2 = choices_visual[c2]

                # Определение победителя
                winner_text = ""
                if c1 == c2:
                    winner_text = "🤝 <b>Результат:</b> Боевая ничья!"
                elif (c1 == 'rock' and c2 == 'scissors') or (c1 == 'scissors' and c2 == 'paper') or (c1 == 'paper' and c2 == 'rock'):
                    winner_text = f"🏆 Победитель: <b>{game['p1_name']} {emoji1}</b> ! (побил {emoji2})"
                else:
                    winner_text = f"🏆 Победитель: <b>{game['p2_name']} {emoji2}</b> ! (побил {emoji1})"

                text = f"✂️ <b>Камень, Ножницы, Бумага — Финал!</b>\n" \
                       f"───────────────────────────────────\n" \
                       f"👤 {game['p1_name']} выбрал: {emoji1}\n" \
                       f"👤 {game['p2_name']} выбрал: {emoji2}\n\n" \
                       f"{winner_text}"
                buttons = None

            try:
                await event.edit(text, buttons=buttons)
            except Exception as e:
                print(f"Error editing RPS game board: {e}")

    async def init(self, client, command_prefix, events, load_module,
        loaded_modules, config, config_path, install_package, bot_start_time):
        self.client = client
        self.prefix = command_prefix
        self.config = config

        async def rps_handler(event):
            if not event.text:
                return
            if event.text.strip() != f'{self.prefix}rps':
                return
            if not event.is_reply:
                await event.edit("<b>❌ Ошибка: Ответьте (сделайте реплай) этой командой на сообщение оппонента!</b>")
                return

            bot_username = self.config.get('InlineBot', 'username', fallback='')
            bot_token = self.config.get('InlineBot', 'token', fallback='')
            if not bot_username or not bot_token:
                await event.edit('❌ Inline-бот не настроен!')
                return

            reply_msg = await event.get_reply_message()
            opponent_id = reply_msg.sender_id
            me = await self.client.get_me()

            if opponent_id == me.id:
                await event.edit("<b>❌ Нельзя играть в Камень, Ножницы, Бумага с самим собой!</b>")
                return

            # Генерируем уникальный инлайн запрос
            import time
            rps_query = f"rps_duel_{opponent_id}_{int(time.time())}"

            try:
                bot = await self.client.get_entity(bot_username)
                result = await self.client.inline_query(bot, rps_query)
                await result[0].click(event.chat_id, reply_to=event.reply_to_msg_id)
                await event.delete()
            except Exception as e:
                await event.edit(f'❌ Ошибка вызова игры: {str(e)}')

        client.add_event_handler(rps_handler, events.NewMessage(outgoing=True))
