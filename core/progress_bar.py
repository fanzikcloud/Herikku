import asyncio


class ProgressBar:

    def __init__(self, message, total, prefix='', suffix='', length=20,
        fill='█', empty='░'):
        self.message = message
        self.total = total
        self.current = 0
        self.prefix = prefix
        self.suffix = suffix
        self.length = length
        self.fill = fill
        self.empty = empty
        self.last_update = 0

    async def update(self, current, text=''):
        self.current = current
        import time
        now = time.time()
        if now - self.last_update < 1 and current < self.total:
            return
        self.last_update = now
        percent = min(100, int(100 * (current / float(self.total))))
        filled_length = int(self.length * current // self.total)
        bar = self.fill * filled_length + self.empty * (self.length -
            filled_length)
        progress_text = f'{self.prefix}\n\n'
        progress_text += f'[{bar}] {percent}%\n\n'
        if text:
            progress_text += f'{text}\n\n'
        progress_text += f'{self.suffix}'
        try:
            await self.message.edit(progress_text)
        except:
            pass

    async def finish(self, text='✅ Готово!'):
        bar = self.fill * self.length
        progress_text = f'{self.prefix}\n\n'
        progress_text += f'[{bar}] 100%\n\n'
        progress_text += f'{text}'
        try:
            await self.message.edit(progress_text)
        except:
            pass


class SpinnerProgress:
    FRAMES = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']

    def __init__(self, message, text='Обработка...'):
        self.message = message
        self.text = text
        self.running = False
        self.task = None
        self.frame = 0

    async def start(self):
        self.running = True
        self.task = asyncio.create_task(self._animate())

    async def _animate(self):
        while self.running:
            frame = self.FRAMES[self.frame % len(self.FRAMES)]
            try:
                await self.message.edit(f'{frame} {self.text}')
            except:
                pass
            self.frame += 1
            await asyncio.sleep(0.2)

    async def stop(self, final_text='✅ Готово!'):
        self.running = False
        if self.task:
            self.task.cancel()
        try:
            await self.message.edit(final_text)
        except:
            pass
