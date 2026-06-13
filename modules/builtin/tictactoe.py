from core.base_module import Module
import json
import random
from telethon import events, Button


class TicTacToeModule(Module):
    NAME = 'TicTacToe'
    AUTHOR = 'Herikku'
    DESCRIPTION = 'Игра в Крестики-Нолики 3х3 через Inline-бота (команда .krestnolik в ответ на СМС)'
    DEPENDENCIES = []
    COMMANDS = {
        'krestnolik': 'Отправить дуэль в крестики-нолики (нужно ответить на СМС оппонента)'
    }
    CONFIG_ICON = '❌'

    # База данных активных игр в оперативной памяти:
    # { game_id: { 'player1': id, 'player2': id, 'turn': id, 'board': [...], 'p1_symbol': '❌', 'p2_symbol': '⭕', 'status': 'waiting/active/won/draw' } }
    GAMES = {}

    @staticmethod
    async def INLINE_HANDLERS(bot_client, events, config, loaded_modules):
        owner_id = None

        @bot_client.on(events.InlineQuery)
        async def ttt_inline_query(event):
            nonlocal owner_id
            query = event.text.strip()
            if not query.startswith('ttt_duel_'):
                return
                
            if owner_id is None:
                owner_id = event.sender_id
                
            if event.sender_id != owner_id:
                await event.answer([])
                return

            # Формат запроса: ttt_duel_{opponent_id}_{random_id}
            parts = query.split('_')
            if len(parts) < 4:
                return

            opponent_id = int(parts[2])
            game_id = query

            builder = event.builder
            text = f"⚔️ <b>Дуэль в Крестики-Нолики!</b>\n\n" \
                   f"Вызов брошен пользователю с ID: <code>{opponent_id}</code>\n" \
                   f"<i>Оппонент должен нажать на кнопку ниже, чтобы принять вызов!</i>"

            buttons = [[Button.inline("⚔️ Принять вызов", f"ttt_accept_{opponent_id}_{owner_id}")]]
            result = builder.article(
                title="⚔️ Крестики-Нолики: Дуэль!",
                text=text,
                buttons=buttons
            )
            await event.answer([result], cache_time=0)

        # Обработчик нажатия на кнопку "Принять вызов" и ходов на игровом поле
        @bot_client.on(events.CallbackQuery(pattern=b'ttt_'))
        async def ttt_callback_handler(event):
            data = event.data.decode('utf-8')
            
            # 1. ПРИНЯТИЕ ДУЭЛИ
            if data.startswith('ttt_accept_'):
                # Формат: ttt_accept_{opponent_id}_{owner_id}
                parts = data.split('_')
                opponent_id = int(parts[2])
                p1_id = int(parts[3]) # создатель игры (owner_id)
                p2_id = event.sender_id # тот, кто нажимает (opponent_id)

                if p2_id != opponent_id:
                    await event.answer("❌ Этот вызов брошен не вам!", alert=True)
                    return

                # Создаем уникальный ID игры на основе сообщения
                game_key = f"{event.chat_id}_{event.message_id}"
                
                # Инициализация игры
                # ❌ ходят первыми
                TicTacToeModule.GAMES[game_key] = {
                    'p1': p1_id,
                    'p2': p2_id,
                    'p1_name': (await bot_client.get_entity(p1_id)).first_name,
                    'p2_name': (await bot_client.get_entity(p2_id)).first_name,
                    'turn': p1_id, # первый ход за создателем
                    'board': [' ' for _ in range(9)],
                    'status': 'active'
                }

                await event.answer("🎮 Игра началась! Ваш ход, Крестики!", alert=True)
                await draw_board(event, game_key)

            # 2. ИГРОВОЙ ХОД
            elif data.startswith('ttt_move_'):
                # Формат: ttt_move_{index}_{game_key} (в качестве game_key выступает chat_id_message_id)
                parts = data.split('_')
                cell_index = int(parts[2])
                game_key = f"{parts[3]}_{parts[4]}"

                game = TicTacToeModule.GAMES.get(game_key)
                if not game:
                    await event.answer("⚠️ Игра не найдена или уже завершена!", alert=True)
                    return

                if game['status'] != 'active':
                    await event.answer("🎮 Игра уже завершена!", alert=True)
                    return

                current_player = event.sender_id
                if current_player != game['turn']:
                    await event.answer("⏳ Сейчас не ваш ход!", alert=True)
                    return

                if game['board'][cell_index] != ' ':
                    await event.answer("❌ Эта ячейка уже занята!", alert=True)
                    return

                # Определяем символ игрока (p1 всегда Крестик, p2 всегда Нолик)
                symbol = '❌' if current_player == game['p1'] else '⭕'
                game['board'][cell_index] = symbol

                # Проверяем победу или ничью
                winner_symbol = check_winner(game['board'])
                if winner_symbol:
                    game['status'] = 'won'
                    winner_name = game['p1_name'] if winner_symbol == '❌' else game['p2_name']
                    await event.answer(f"🎉 {winner_name} победил!", alert=True)
                elif ' ' not in game['board']:
                    game['status'] = 'draw'
                    await event.answer("🤝 Ничья!", alert=True)
                else:
                    # Передаем ход оппоненту
                    game['turn'] = game['p2'] if current_player == game['p1'] else game['p1']
                    await event.answer("✅ Ход сделан!")

                await draw_board(event, game_key)

        # Функция отрисовки игрового поля
        async def draw_board(event, game_key):
            game = TicTacToeModule.GAMES.get(game_key)
            if not game:
                return

            board = game['board']
            
            # Создаем сетку кнопок 3х3
            buttons = []
            for row in range(3):
                row_buttons = []
                for col in range(3):
                    idx = row * 3 + col
                    val = board[idx]
                    display_val = val if val != ' ' else '🔹'
                    # ttt_move_{index}_{chat_id}_{message_id}
                    callback_data = f"ttt_move_{idx}_{game_key}"
                    row_buttons.append(Button.inline(display_val, callback_data))
                buttons.append(row_buttons)

            # Формируем статус-сообщение
            p1_mark = "❌"
            p2_mark = "⭕"

            if game['status'] == 'active':
                current_turn_name = game['p1_name'] if game['turn'] == game['p1'] else game['p2_name']
                current_mark = p1_mark if game['turn'] == game['p1'] else p2_mark
                status_text = f"🎮 <b>Крестики-Нолики 3х3</b>\n" \
                              f"─────────────────────\n" \
                              f"❌ <b>Крестик:</b> {game['p1_name']}\n" \
                              f"⭕ <b>Нолик:</b> {game['p2_name']}\n\n" \
                              f"👉 Ходит: {current_turn_name} {current_mark}"
            elif game['status'] == 'won':
                winner_name = game['p1_name'] if game['turn'] == game['p1'] else game['p2_name']
                winner_mark = p1_mark if game['turn'] == game['p1'] else p2_mark
                status_text = f"🎮 <b>Крестики-Нолики 3х3 — Конец игры!</b>\n" \
                              f"─────────────────────\n" \
                              f"❌ <b>Крестик:</b> {game['p1_name']}\n" \
                              f"⭕ <b>Нолик:</b> {game['p2_name']}\n\n" \
                              f"🎉 <b>Победитель:</b> {winner_name} {winner_mark} !"
            else: # draw
                status_text = f"🎮 <b>Крестики-Нолики 3х3 — Конец игры!</b>\n" \
                              f"─────────────────────\n" \
                              f"❌ <b>Крестик:</b> {game['p1_name']}\n" \
                              f"⭕ <b>Нолик:</b> {game['p2_name']}\n\n" \
                              f"🤝 <b>Результат:</b> Боевая ничья!"

            try:
                await event.edit(status_text, buttons=buttons)
            except Exception as e:
                print(f"Error editing TicTacToe board: {e}")

        # Функция проверки победителя
        def check_winner(board):
            win_coords = [
                (0, 1, 2), (3, 4, 5), (6, 7, 8), # горизонтали
                (0, 3, 6), (1, 4, 7), (2, 5, 8), # вертикали
                (0, 4, 8), (2, 4, 6)             # диагонали
            ]
            for coord in win_coords:
                if board[coord[0]] == board[coord[1]] == board[coord[2]] != ' ':
                    return board[coord[0]]
            return None

    async def init(self, client, command_prefix, events, load_module,
        loaded_modules, config, config_path, install_package, bot_start_time):
        self.client = client
        self.prefix = command_prefix
        self.config = config

        async def krestnolik_handler(event):
            if not event.text:
                return
            if event.text.strip() != f'{self.prefix}krestnolik':
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
                await event.edit("<b>❌ Нельзя играть в крестики-нолики с самим собой!</b>")
                return

            # Генерируем уникальный инлайн запрос: ttt_duel_{opponent_id}_{random_id}
            import time
            ttt_query = f"ttt_duel_{opponent_id}_{int(time.time())}"

            try:
                bot = await self.client.get_entity(bot_username)
                result = await self.client.inline_query(bot, ttt_query)
                await result[0].click(event.chat_id, reply_to=event.reply_to_msg_id)
                await event.delete()
            except Exception as e:
                await event.edit(f'❌ Ошибка вызова игры: {str(e)}')

        client.add_event_handler(krestnolik_handler, events.NewMessage(outgoing=True))
