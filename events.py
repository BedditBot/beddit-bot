from custom import *

bot = config.bot


@bot.event
async def on_ready():
    await ensure_prefixes_integrity()

    clear_active_bets()

    latency = round(bot.latency, 3) * 1000  # in ms to 3 d.p.

    print(f"Connected successfully as {bot.user} ({latency}ms).")


@bot.event
async def on_guild_join(guild):
    await set_guild_prefixes(guild)


@bot.event
async def on_guild_remove(guild):
    remove_guild_prefixes(guild)
