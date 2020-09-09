import json

# Discord
D_TOKEN = None

bot = None


def set_bot():
    from discord.ext import commands

    # for custom server-specific prefixes
    def get_prefix(_, message):
        with open("prefixes.json", "r") as file:
            file_prefixes = json.load(file)

        return file_prefixes[str(message.guild.id)]

    global bot
    bot = commands.Bot(command_prefix=get_prefix)


set_bot()

# Reddit
R_CLIENT_ID = None
R_CLIENT_SECRET = None
R_USERNAME = None
R_PASSWORD = None
R_USER_AGENT = None
