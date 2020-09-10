# Discord
D_TOKEN = None

bot = None


def set_bot():
    from discord.ext import commands

    # for custom server-specific prefixes
    def get_prefix(_, message):
        from custom import get_prefixes_data

        prefixes_data = get_prefixes_data()

        return prefixes_data[message.guild.id]

    global bot
    bot = commands.Bot(command_prefix=get_prefix)


set_bot()

# Reddit
R_CLIENT_ID = None
R_CLIENT_SECRET = None
R_USERNAME = None
R_PASSWORD = None
R_USER_AGENT = None
