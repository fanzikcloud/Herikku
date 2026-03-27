from core.base_module import Module
import pickle
import configparser


class RPModule(Module):
    NAME = 'RPMod'
    AUTHOR = '@trololo_1'
    DESCRIPTION = 'Модуль для ролевых команд (RP)'
    DEPENDENCIES = ['emoji']
    COMMANDS = {'dobrp <команда> / <действие> / <эмодзи>':
        'Добавить RP команду', 'delrp <команда>':
        "Удалить RP команду (или 'all' для всех)", 'rplist':
        'Список всех RP команд', 'rpmod': 'Включить/выключить RP режим',
        'rpmod toggle': 'Переключить режим отправки/редактирования',
        'rpnick <ник>': 'Установить свой RP ник', 'rpback -b':
        'Создать бекап RP команд', 'rpback -r':
        'Загрузить бекап (с реплаем на файл)', 'rpblock':
        'Добавить/удалить чат в исключения', 'rpblock list':
        'Список чатов в исключениях', 'useraccept <id/reply>':
        'Управление доступом к командам', 'rpconf': 'Настройка шаблона для RP'}

    async def init(self, client, command_prefix, events, load_module,
        loaded_modules, config, config_path, install_package, bot_start_time):
        self.client = client
        self.prefix = command_prefix
        self.config_path = config_path
        self.config = configparser.ConfigParser()
        self.config.read(config_path, encoding='utf-8')
        if not self.config.has_section('RPMod'):
            self.config.add_section('RPMod')
        self._init_config()
        self._save_config()
        client.add_event_handler(self.dobrp_handler, events.NewMessage(
            outgoing=True, pattern=f'^\\{self.prefix}dobrp'))
        client.add_event_handler(self.delrp_handler, events.NewMessage(
            outgoing=True, pattern=f'^\\{self.prefix}delrp'))
        client.add_event_handler(self.rplist_handler, events.NewMessage(
            outgoing=True, pattern=f'^\\{self.prefix}rplist'))
        client.add_event_handler(self.rpmod_handler, events.NewMessage(
            outgoing=True, pattern=f'^\\{self.prefix}rpmod'))
        client.add_event_handler(self.rpnick_handler, events.NewMessage(
            outgoing=True, pattern=f'^\\{self.prefix}rpnick'))
        client.add_event_handler(self.rpback_handler, events.NewMessage(
            outgoing=True, pattern=f'^\\{self.prefix}rpback'))
        client.add_event_handler(self.rpblock_handler, events.NewMessage(
            outgoing=True, pattern=f'^\\{self.prefix}rpblock'))
        client.add_event_handler(self.useraccept_handler, events.NewMessage
            (outgoing=True, pattern=f'^\\{self.prefix}useraccept'))
        client.add_event_handler(self.rpconf_handler, events.NewMessage(
            outgoing=True, pattern=f'^\\{self.prefix}rpconf'))
        client.add_event_handler(self.rp_watcher, events.NewMessage())

    def _init_config(self):
        import json
        if not self.config.get('RPMod', 'status', fallback=None):
            self.config.set('RPMod', 'status', '1')
        if not self.config.get('RPMod', 'rprezjim', fallback=None):
            self.config.set('RPMod', 'rprezjim', '1')
        if not self.config.get('RPMod', 'exlist', fallback=None):
            self.config.set('RPMod', 'exlist', json.dumps([]))
        if not self.config.get('RPMod', 'rpnicks', fallback=None):
            self.config.set('RPMod', 'rpnicks', json.dumps({}))
        if not self.config.get('RPMod', 'rpcomands', fallback=None):
            default_commands = {'чмок': 'чмокнул', 'лизь': 'лизнул', 'кусь':
                'кусьнул', 'поцеловать': 'поцеловал', 'обнять': 'обнял',
                'погладить': 'погладил'}
            self.config.set('RPMod', 'rpcomands', json.dumps(default_commands))
        if not self.config.get('RPMod', 'rpemoji', fallback=None):
            self.config.set('RPMod', 'rpemoji', json.dumps({'лизь': '👅'}))
        if not self.config.get('RPMod', 'useraccept', fallback=None):
            self.config.set('RPMod', 'useraccept', json.dumps([]))
        if not self.config.get('RPMod', 'rpconfigurate', fallback=None):
            conf_default = {'-s1': {'1': [True, '<b>жирный</b>', '<b>',
                '</b>'], '2': [False, '<i>курсив</i>', '<i>', '</i>'], '3':
                [False, '<u>подчеркнутый</u>', '<u>', '</u>']}, '-s2': {'1':
                [False, '<b>жирный</b>', '<b>', '</b>'], '2': [False,
                '<i>курсив</i>', '<i>', '</i>'], '3': [False,
                '<u>подчеркнутый</u>', '<u>', '</u>']}, '-sE': {'1': [True,
                '💬'], '2': [False, '💭'], '3': [False, '🗯'], '4': [False,
                '✉️']}, '-sS': {'1': [True, 'пробел', ' '], '2': [False,
                'разрыв строки', '\n'], '3': [False, 'точка + пробел', '. '
                ], '4': [False, 'запятая + пробел', ', ']}}
            self.config.set('RPMod', 'rpconfigurate', json.dumps(conf_default))

    def _save_config(self):
        with open(self.config_path, 'w', encoding='utf-8') as f:
            self.config.write(f)

    def _get_json_config(self, key):
        import json
        return json.loads(self.config.get('RPMod', key, fallback='{}'))

    def _set_json_config(self, key, value):
        import json
        self.config.set('RPMod', key, json.dumps(value))
        self._save_config()

    async def dobrp_handler(self, event):
        import emoji
        import string
        args = event.text[len(f'{self.prefix}dobrp'):].strip()
        dict_rp = self._get_json_config('rpcomands')
        try:
            parts = args.split('/')
            key_rp = parts[0].strip()
            value_rp = parts[1].strip() if len(parts) > 1 else None
            emoji_rp = parts[2].strip() if len(parts) > 2 else None
            if not key_rp:
                await event.edit('<b>Вы не ввели название рп команды.</b>')
                return
            if not value_rp:
                await event.edit('<b>Вы не ввели действие для рп команды.</b>')
                return
            if len(key_rp.split()) > 1:
                await event.edit(
                    '<b>В качестве рп команды было введено больше одного слова.</b>'
                    )
                return
            if key_rp == 'all':
                await event.edit(
                    "<b>Использовать '<code>all</code>' в качестве названия команды запрещено!</b>"
                    )
                return
            if len(dict_rp) >= 70:
                await event.edit('<b>Достигнут лимит рп команд (70).</b>')
                return
            if emoji_rp:
                try:
                    emoji_count = emoji.emoji_count(emoji_rp)
                    if emoji_count > 3:
                        await event.edit('<b>Было введено более 3 эмодзи.</b>')
                        return
                except:
                    pass
                dict_emoji_rp = self._get_json_config('rpemoji')
                dict_emoji_rp[key_rp] = emoji_rp
                self._set_json_config('rpemoji', dict_emoji_rp)
                dict_rp[key_rp] = value_rp
                self._set_json_config('rpcomands', dict_rp)
                await event.edit(
                    f"<b>Команда '<code>{key_rp}</code>' успешно добавлена с эмодзи '{emoji_rp}'!</b>"
                    )
            else:
                dict_rp[key_rp] = value_rp
                self._set_json_config('rpcomands', dict_rp)
                await event.edit(
                    f"<b>Команда '<code>{key_rp}</code>' успешно добавлена!</b>"
                    )
        except Exception as e:
            await event.edit(
                f"""<b>Ошибка: {str(e)}</b>

Использование: <code>{self.prefix}dobrp команда / действие / эмодзи</code>"""
                )

    async def delrp_handler(self, event):
        args = event.text[len(f'{self.prefix}delrp'):].strip()
        dict_rp = self._get_json_config('rpcomands')
        dict_emoji_rp = self._get_json_config('rpemoji')
        if not args:
            await event.edit('<b>Вы не ввели команду.</b>')
            return
        if args == 'all':
            self._set_json_config('rpcomands', {})
            self._set_json_config('rpemoji', {})
            await event.edit('<b>Список рп команд очищен.</b>')
            return
        if args in dict_rp:
            del dict_rp[args]
            if args in dict_emoji_rp:
                del dict_emoji_rp[args]
                self._set_json_config('rpemoji', dict_emoji_rp)
            self._set_json_config('rpcomands', dict_rp)
            await event.edit(
                f"<b>Команда '<code>{args}</code>' успешно удалена!</b>")
        else:
            await event.edit('<b>Команда не найдена.</b>')

    async def rplist_handler(self, event):
        com = self._get_json_config('rpcomands')
        emojies = self._get_json_config('rpemoji')
        if not com:
            await event.edit('<b>Увы, у вас нету рп команд. :(</b>')
            return
        message = f'У вас рп команд: <b>{len(com)}</b> из <b>70</b>.\n'
        for cmd, action in com.items():
            if cmd in emojies:
                message += (
                    f'\n• <b><code>{cmd}</code> - {action} |</b> {emojies[cmd]}'
                    )
            else:
                message += f'\n• <b><code>{cmd}</code> - {action}</b>'
        await event.edit(message)

    async def rpmod_handler(self, event):
        args = event.text[len(f'{self.prefix}rpmod'):].strip()
        status = int(self.config.get('RPMod', 'status', fallback='1'))
        rezjim = int(self.config.get('RPMod', 'rprezjim', fallback='1'))
        if not args:
            if status == 1:
                self.config.set('RPMod', 'status', '2')
                await event.edit('<b>RP Режим <code>выключен</code></b>')
            else:
                self.config.set('RPMod', 'status', '1')
                await event.edit('<b>RP Режим <code>включен</code></b>')
            self._save_config()
        elif args == 'toggle':
            if rezjim == 1:
                self.config.set('RPMod', 'rprezjim', '2')
                await event.edit(
                    '<b>RP Режим изменён на <code>отправку смс.</code></b>')
            else:
                self.config.set('RPMod', 'rprezjim', '1')
                await event.edit(
                    '<b>RP Режим изменён на <code>изменение смс.</code></b>')
            self._save_config()
        else:
            await event.edit('Что-то не так..')

    async def rpnick_handler(self, event):
        import emoji
        args = event.text[len(f'{self.prefix}rpnick'):].strip()
        nicks = self._get_json_config('rpnicks')
        me = await self.client.get_me()
        if not args:
            nicks[str(me.id)] = me.first_name
            self._set_json_config('rpnicks', nicks)
            await event.edit(f'<b>Ник изменён на {me.first_name}</b>')
            return
        try:
            emoji_count = emoji.emoji_count(args)
            if emoji_count > 3:
                await event.edit(f'<b>Ник содержит более трёх эмодзи.</b>')
                return
        except:
            pass
        if len(args) >= 45:
            await event.edit(f'<b>Ник превышает лимит в 45 символов.</b>')
            return
        nicks[str(me.id)] = args
        self._set_json_config('rpnicks', nicks)
        await event.edit(f'<b>Ник изменён на {args}</b>')

    async def rpback_handler(self, event):
        args = event.text[len(f'{self.prefix}rpback'):].strip()
        if not args:
            await event.edit(
                """<b>Аргументы:</b>
<code>-b</code> <b>-- сделать бекап.</b>
<code>-r</code> <b>загрузить бекап.(используй с реплаем на файл)</b>"""
                )
            return
        if args == '-b':
            try:
                comands = self._get_json_config('rpcomands')
                emojies = self._get_json_config('rpemoji')
                file_name = 'RPModBackUp.pickle'
                dict_all = {'rp': comands, 'emj': emojies}
                with open(file_name, 'wb') as f:
                    pickle.dump(dict_all, f)
                await event.delete()
                await self.client.send_file(event.chat_id, file_name)
            except Exception as e:
                await event.edit(f'<b>Ошибка:\n</b>{e}')
        elif args == '-r':
            reply = await event.get_reply_message()
            if not reply or not reply.document:
                await event.edit('<b>Ответьте на файл с бекапом!</b>')
                return
            try:
                file_name = 'RPModBackUp.pickle'
                await reply.download_media(file_name)
                with open(file_name, 'rb') as f:
                    data = pickle.load(f)
                comands = self._get_json_config('rpcomands')
                emojies = self._get_json_config('rpemoji')
                comands.update(data['rp'])
                emojies.update(data['emj'])
                self._set_json_config('rpcomands', comands)
                self._set_json_config('rpemoji', emojies)
                await event.edit('<b>Команды обновлены!</b>')
            except Exception as e:
                await event.edit(f'<b>Ошибка:\n</b>{e}')

    async def rpblock_handler(self, event):
        args = event.text[len(f'{self.prefix}rpblock'):].strip()
        ex = self._get_json_config('exlist')
        if not args:
            chat = await event.get_chat()
            chat_id = chat.id
            if chat_id in ex:
                ex.remove(chat_id)
                self._set_json_config('exlist', ex)
                chat_name = getattr(chat, 'title', getattr(chat,
                    'first_name', 'Unknown'))
                await event.edit(
                    f'<i>Чат <b><u>{chat_name}</u></b>[<code>{chat_id}</code>] удален из исключений.</i>'
                    )
            else:
                ex.append(chat_id)
                self._set_json_config('exlist', ex)
                chat_name = getattr(chat, 'title', getattr(chat,
                    'first_name', 'Unknown'))
                await event.edit(
                    f'<i>Чат <b><u>{chat_name}</u></b>[<code>{chat_id}</code>] добавлен в исключения.</i>'
                    )
        elif args == 'list':
            if not ex:
                await event.edit('<b>Список исключений пуст.</b>')
                return
            message = f'<i>Чаты, которые есть в исключениях ({len(ex)}):</i>\n'
            for chat_id in ex:
                try:
                    chat = await self.client.get_entity(chat_id)
                    chat_name = getattr(chat, 'title', getattr(chat,
                        'first_name', 'Unknown'))
                    message += (
                        f'\n• <b><u>{chat_name}</u> --- </b><code>{chat_id}</code>'
                        )
                except:
                    message += (
                        f'\n• <code>{chat_id}</code> (не удалось получить)')
            await event.edit(message)
        elif args.lstrip('-').isdigit():
            chat_id = int(args)
            if chat_id in ex:
                ex.remove(chat_id)
                self._set_json_config('exlist', ex)
                await event.edit(
                    f'<i>Чат <code>{chat_id}</code> удален из исключений.</i>')
            else:
                ex.append(chat_id)
                self._set_json_config('exlist', ex)
                await event.edit(
                    f'<i>Чат <code>{chat_id}</code> добавлен в исключения.</i>'
                    )

    async def useraccept_handler(self, event):
        args = event.text[len(f'{self.prefix}useraccept'):].strip()
        reply = await event.get_reply_message()
        userA = self._get_json_config('useraccept')
        if args == '-l':
            if not userA:
                await event.edit('<b>Список пуст.</b>')
                return
            message = (
                '<b>Пользователи, у которых есть доступ к командам:</b>\n')
            for user_id in userA:
                try:
                    user = await self.client.get_entity(int(user_id))
                    message += (
                        f'\n<b>• <u>{user.first_name}</u> ---</b> <code>{user_id}</code>'
                        )
                except:
                    message += f'\n<b>•</b> <code>{user_id}</code>'
            await event.edit(message)
            return
        user_id = None
        if args and args.isdigit():
            user_id = int(args)
        elif reply:
            user_id = reply.sender_id
        else:
            await event.edit(
                '<b>Укажите ID или ответьте на сообщение пользователя.</b>')
            return
        if user_id in userA:
            userA.remove(user_id)
            self._set_json_config('useraccept', userA)
            await event.edit(
                f'<b>Пользователю <code>{user_id}</code> был закрыт доступ.</b>'
                )
        else:
            userA.append(user_id)
            self._set_json_config('useraccept', userA)
            await event.edit(
                f'<b>Пользователю <code>{user_id}</code> был открыт доступ.</b>'
                )

    async def rpconf_handler(self, event):
        args = event.text[len(f'{self.prefix}rpconf'):].strip()
        conf = self._get_json_config('rpconfigurate')
        if not args:
            message = '⚙️ <b>Настройка шаблона для команды:</b>\n\n'
            for section, items in conf.items():
                if section == '-s1':
                    message += '<code>-s1</code> --- стиль для "С репликой":\n'
                elif section == '-s2':
                    message += '\n<code>-s2</code> --- стиль для реплики:\n'
                elif section == '-sE':
                    message += (
                        '\n<code>-sE</code> --- эмодзи перед репликой:\n')
                elif section == '-sS':
                    message += '\n<code>-sS</code> --- разрыв строк:\n'
                for key, value in items.items():
                    status = '✅' if value[0] else '❌'
                    message += f'{key} | {value[1]} | {status}\n'
            message += (
                f'\n<b>Пример:</b> <code>{self.prefix}rpconf -s1 2</code>')
            await event.edit(message)
            return
        parts = args.split()
        if len(parts) < 2:
            await event.edit('<b>Недостаточно аргументов.</b>')
            return
        section = parts[0]
        option = parts[1]
        if section not in conf or option not in conf[section]:
            await event.edit('<b>Неверные параметры.</b>')
            return
        if section in ['-s1', '-s2']:
            conf[section][option][0] = not conf[section][option][0]
        elif section in ['-sE', '-sS']:
            for key in conf[section]:
                conf[section][key][0] = False
            conf[section][option][0] = True
        self._set_json_config('rpconfigurate', conf)
        await event.edit('<b>Конфигурация успешно изменена.</b>')

    async def rp_watcher(self, event):
        try:
            status = int(self.config.get('RPMod', 'status', fallback='1'))
            if status != 1:
                return
            comands = self._get_json_config('rpcomands')
            rezjim = int(self.config.get('RPMod', 'rprezjim', fallback='1'))
            emojies = self._get_json_config('rpemoji')
            ex = self._get_json_config('exlist')
            nicks = self._get_json_config('rpnicks')
            users_accept = self._get_json_config('useraccept')
            conf = self._get_json_config('rpconfigurate')
            chat = await event.get_chat()
            if chat.id in ex:
                return
            me = await self.client.get_me()
            if (event.sender_id not in users_accept and event.sender_id !=
                me.id):
                return
            if not event.text:
                return
            sender = await self.client.get_entity(event.sender_id)
            nick = nicks.get(str(sender.id), sender.first_name)
            lines = event.text.splitlines()
            tags = lines[0].split(' ')
            if not tags[-1].startswith('@'):
                reply = await event.get_reply_message()
                if not reply:
                    return
                user = await self.client.get_entity(reply.sender_id)
            else:
                try:
                    if tags[-1][1:].isdigit():
                        user = await self.client.get_entity(int(tags[-1][1:]))
                    else:
                        user = await self.client.get_entity(tags[-1])
                    lines[0] = lines[0].rsplit(' ', 1)[0]
                except:
                    return
            detail = lines[0].split(' ', maxsplit=1)
            if len(detail) < 1 or detail[0] not in comands:
                return
            if len(detail) < 2:
                detail.append('')
            user_nick = nicks.get(str(user.id), user.first_name)
            sE = ''.join([(value[1] if value[0] else '') for value in conf[
                '-sE'].values()])
            s1_open = ''.join([(value[2] if value[0] else '') for value in
                conf['-s1'].values()])
            s1_close = ''.join([(value[3] if value[0] else '') for value in
                reversed(list(conf['-s1'].values()))])
            s2_open = ''.join([(value[2] if value[0] else '') for value in
                conf['-s2'].values()])
            s2_close = ''.join([(value[3] if value[0] else '') for value in
                reversed(list(conf['-s2'].values()))])
            sS = ''.join([(value[2] if value[0] else '') for value in conf[
                '-sS'].values()])
            rp_message = ''
            if detail[0] in emojies:
                rp_message += emojies[detail[0]] + ' | '
            rp_message += (
                f'<a href="tg://user?id={sender.id}">{nick}</a> {comands[detail[0]]} <a href="tg://user?id={user.id}">{user_nick}</a>'
                )
            if detail[1]:
                rp_message += ' ' + detail[1]
            if len(lines) >= 2:
                rp_message += f"""
{sE} {s1_open}С репликой: {s1_close}{s2_open}{sS.join(lines[1:])}{s2_close}"""
            if rezjim == 1:
                await event.edit(rp_message)
            else:
                await event.respond(rp_message)
        except Exception:
            pass
