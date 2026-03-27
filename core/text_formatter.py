class TextFormatter:
    COLORS = {'red': '\x1b[91m', 'green': '\x1b[92m', 'yellow': '\x1b[93m',
        'blue': '\x1b[94m', 'magenta': '\x1b[95m', 'cyan': '\x1b[96m',
        'white': '\x1b[97m', 'reset': '\x1b[0m', 'bold': '\x1b[1m'}

    @staticmethod
    def color(text, color):
        return (
            f"{TextFormatter.COLORS.get(color, '')}{text}{TextFormatter.COLORS['reset']}"
            )

    @staticmethod
    def gradient(text, start_color='cyan', end_color='magenta'):
        return (
            f"{TextFormatter.COLORS.get(start_color, '')}{text}{TextFormatter.COLORS['reset']}"
            )

    @staticmethod
    def bold(text):
        return (
            f"{TextFormatter.COLORS['bold']}{text}{TextFormatter.COLORS['reset']}"
            )
