# Discord
D_TOKEN = None

bot = None


def set_bot():
    from discord.ext import commands

    global bot
    bot = commands.Bot(command_prefix="&")


set_bot()

# Reddit
R_CLIENT_ID = None
R_CLIENT_SECRET = None
R_USERNAME = None
R_PASSWORD = None
R_USER_AGENT = None
