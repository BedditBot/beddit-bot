import config

bot = config.bot


@bot.event
async def on_ready():
    latency = round(bot.latency, 3) * 1000  # in ms to 3 d.p.

    print(f"Connected successfully as {bot.user} ({latency}ms).")


@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.content.strip(" ").lower() == "ping?":
        latency = round(bot.latency, 3) * 1000  # in ms to 3 d.p.

        await message.channel.send(f"Pong! ({latency}ms)")

    await bot.process_commands(message)
