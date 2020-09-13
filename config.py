# database
DATABASE_URL = None

connection = None

# Discord
D_TOKEN = None

bot = None


def set_bot():
    from discord.ext import commands

    # for custom server-specific prefixes
    def get_prefix(_, message):
        from custom import get_guild_prefixes

        guild_prefixes = get_guild_prefixes(message.guild)

        return guild_prefixes["prefixes"]

    global bot
    bot = commands.Bot(command_prefix=get_prefix)


set_bot()

# Reddit
R_CLIENT_ID = None
R_CLIENT_SECRET = None
R_USERNAME = None
R_PASSWORD = None
R_USER_AGENT = None
