class Module:
    NAME = 'Base Module'
    AUTHOR = 'Unknown'
    DESCRIPTION = 'Base module class'
    DEPENDENCIES = []
    COMMANDS = {}
    CONFIG_HANDLER = None
    CONFIG_ICON = '⚙️'
    INLINE_HANDLERS = None

    async def init(self, client, command_prefix, events, load_module,
        loaded_modules, config, config_path, install_package, bot_start_time):
        raise NotImplementedError('Module must implement init method')

    async def dispose(self):
        pass
