import discord
from discord.ext import commands

# database
DATABASE_URL = None

connection = None

# Discord
D_TOKEN = None


# for custom server-specific prefixes
def get_prefix(_, message):
    from custom import get_guild_prefixes

    guild_prefixes = await get_guild_prefixes(message.guild)

    return guild_prefixes["prefixes"]


intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(
    command_prefix=get_prefix,
    intents=intents
)

bot.allowed_mentions = discord.AllowedMentions(
    everyone=False,
    users=True,
    roles=False,
    replied_user=True
)

# Reddit
R_CLIENT_ID = None
R_CLIENT_SECRET = None
R_USERNAME = None
R_PASSWORD = None
R_USER_AGENT = None
