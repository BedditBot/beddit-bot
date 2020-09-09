import json

import config

bot = config.bot


@bot.event
async def on_ready():
    latency = round(bot.latency, 3) * 1000  # in ms to 3 d.p.

    print(f"Connected successfully as {bot.user} ({latency}ms).")


@bot.event
async def on_guild_join(guild):
    with open("prefixes.json", "r") as file:
        prefixes = json.load(file)

    # sets default prefix ($)
    prefixes[str(guild.id)] = "$"

    with open("prefixes.json", "w") as file:
        json.dump(prefixes, file, indent=4)


@bot.event
async def on_guild_remove(guild):
    with open("prefixes.json", "r") as file:
        prefixes = json.load(file)

    prefixes.pop(str(guild.id))

    with open("prefixes.json", "w") as file:
        json.dump(prefixes, file, indent=4)
