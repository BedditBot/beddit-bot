# Discord
TOKEN = None

bot = None


def set_bot():
    from discord.ext import commands

    global bot
    bot = commands.Bot(command_prefix="&")


set_bot()

# Reddit
CLIENT_ID = None
CLIENT_SECRET = None
USERNAME = None
PASSWORD = None
USER_AGENT = None
