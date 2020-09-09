from custom import get_prefix

# Discord
D_TOKEN = None

bot = None


def set_bot():
    from discord.ext import commands
    from custom import get_prefix

    global bot
    bot = commands.Bot(command_prefix=get_prefix)


set_bot()

# Reddit
R_CLIENT_ID = None
R_CLIENT_SECRET = None
R_USERNAME = None
R_PASSWORD = None
R_USER_AGENT = None
