import config
from custom import get_prefixes, store_prefixes

bot = config.bot


@bot.event
async def on_ready():
    latency = round(bot.latency, 3) * 1000  # in ms to 3 d.p.

    print(f"Connected successfully as {bot.user} ({latency}ms).")


@bot.event
async def on_guild_join(guild):
    prefixes = get_prefixes()

    # sets default prefix ($)
    prefixes[guild.id] = "$"

    store_prefixes(prefixes)


@bot.event
async def on_guild_remove(guild):
    prefixes = get_prefixes()

    prefixes.pop(guild.id)

    store_prefixes(prefixes)
