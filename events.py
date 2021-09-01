from custom import *
from Account import Account
from Accessory import Accessory

bot = config.bot


@bot.event
async def on_ready():
    await Accessory.ensure_integrity()

    await clear_active_bets()

    latency = round(bot.latency, 3) * 1000  # in ms to 3 d.p.

    print(f"Connected successfully as {bot.user} ({latency}ms).")


@bot.event
async def on_guild_join(guild):
    await Accessory.set_prefixes(guild)


@bot.event
async def on_guild_remove(guild):
    await Accessory.remove(guild)
