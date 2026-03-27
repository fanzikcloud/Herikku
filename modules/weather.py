from core.base_module import Module
import aiohttp


class WeatherModule(Module):
    NAME = 'Weather'
    AUTHOR = 'Herikku'
    DESCRIPTION = 'Получение информации о погоде'
    DEPENDENCIES = ['aiohttp']
    COMMANDS = {'weather <город>': 'Показать погоду в указанном городе',
        'w <город>': 'Короткая команда для погоды'}

    async def init(self, client, command_prefix, events, load_module,
        loaded_modules, config, config_path, install_package, bot_start_time):
        self.client = client
        self.prefix = command_prefix

        async def weather_handler(event):
            if not event.text:
                return
            text = event.text
            if not (text.startswith(f'{self.prefix}weather ') or text.
                startswith(f'{self.prefix}w ')):
                return
            if text.startswith(f'{self.prefix}weather '):
                city = text[len(f'{self.prefix}weather '):].strip()
            else:
                city = text[len(f'{self.prefix}w '):].strip()
            if not city:
                await event.edit(
                    f"""**🌤 Погода**

❌ Укажите город!

Использование:
`{self.prefix}weather Москва`
`{self.prefix}w London`"""
                    )
                return
            await event.edit(
                f'**🌤 Погода**\n\n⏳ Получаю данные о погоде в {city}...')
            try:
                url = f'https://wttr.in/{city}?format=j1&lang=ru'
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as response:
                        if response.status != 200:
                            await event.edit(
                                f'**🌤 Погода**\n\n❌ Город не найден: {city}')
                            return
                        data = await response.json()
                current = data['current_condition'][0]
                location = data['nearest_area'][0]
                city_name = location.get('areaName', [{}])[0].get('value', city
                    )
                country = location.get('country', [{}])[0].get('value', '')
                temp = current['temp_C']
                feels_like = current['FeelsLikeC']
                humidity = current['humidity']
                wind_speed = current['windspeedKmph']
                wind_dir = current['winddir16Point']
                pressure = current['pressure']
                visibility = current['visibility']
                uv_index = current['uvIndex']
                weather_desc = current['lang_ru'][0]['value'
                    ] if 'lang_ru' in current else current['weatherDesc'][0][
                    'value']
                weather_code = int(current['weatherCode'])
                weather_emoji = self.get_weather_emoji(weather_code)
                wind_dir_ru = self.get_wind_direction(wind_dir)
                message = f'**🌤 Погода в {city_name}**'
                if country:
                    message += f', {country}'
                message += '\n\n'
                message += f'{weather_emoji} **{weather_desc}**\n\n'
                message += (
                    f'🌡 Температура: **{temp}°C** (ощущается как {feels_like}°C)\n'
                    )
                message += f'💧 Влажность: **{humidity}%**\n'
                message += f'💨 Ветер: **{wind_speed} км/ч** ({wind_dir_ru})\n'
                message += f'🔽 Давление: **{pressure} мбар**\n'
                message += f'👁 Видимость: **{visibility} км**\n'
                message += f'☀️ УФ-индекс: **{uv_index}**'
                await event.edit(message)
            except Exception as e:
                await event.edit(
                    f'**🌤 Погода**\n\n❌ Ошибка получения данных:\n`{str(e)}`')
        client.add_event_handler(weather_handler, events.NewMessage(
            outgoing=True))

    def get_weather_emoji(self, code):
        if code == 113:
            return '☀️'
        elif code in [116, 119, 122]:
            return '⛅'
        elif code in [143, 248, 260]:
            return '🌫'
        elif code in [176, 263, 266, 281, 284, 293, 296]:
            return '🌦'
        elif code in [299, 302, 305, 308, 311, 314, 317, 320, 353, 356, 359]:
            return '🌧'
        elif code in [182, 185, 227, 230, 323, 326, 329, 332, 335, 338, 350,
            362, 365, 368, 371, 374, 377]:
            return '🌨'
        elif code in [386, 389, 392, 395]:
            return '⛈'
        else:
            return '🌤'

    def get_wind_direction(self, direction):
        directions = {'N': 'Север', 'NNE': 'Северо-северо-восток', 'NE':
            'Северо-восток', 'ENE': 'Восточно-северо-восток', 'E': 'Восток',
            'ESE': 'Восточно-юго-восток', 'SE': 'Юго-восток', 'SSE':
            'Южно-юго-восток', 'S': 'Юг', 'SSW': 'Южно-юго-запад', 'SW':
            'Юго-запад', 'WSW': 'Западно-юго-запад', 'W': 'Запад', 'WNW':
            'Западно-северо-запад', 'NW': 'Северо-запад', 'NNW':
            'Северо-северо-запад'}
        return directions.get(direction, direction)
