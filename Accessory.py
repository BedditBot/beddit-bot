import config

bot = config.bot


# rename "prefixes" table to "accessories"

class Accessory:
    def __init__(self, guild_id, prefixes):
        self.guild_id = guild_id
        self.prefixes = prefixes

    @staticmethod
    async def open(guild):
        async with config.connection.transaction():
            await config.connection.execute(
                "INSERT INTO accessories VALUES ($1, $2);",
                guild.id,
                ["$"]  # default prefix
            )

    @staticmethod
    async def get(guild):
        async with config.connection.transaction():
            values = tuple(await config.connection.fetchrow(
                "SELECT * FROM accessories WHERE guild_id = $1;",
                guild.id
            ))

        if not values:
            await Accessory.open(guild)

            async with config.connection.transaction():
                values = tuple(await config.connection.fetchrow(
                    "SELECT * FROM accessories WHERE guild_id = $1;",
                    guild.id
                ))

        return Accessory(*values)

    async def store(self):
        async with config.connection.transaction():
            await config.connection.execute(
                "UPDATE accessories "
                "SET prefixes = $2 "
                "WHERE guild_id = $1;",
                self.guild_id,
                self.prefixes
            )

    @staticmethod
    async def set_prefixes(guild, prefixes_list=None):
        if not prefixes_list:
            # sets default prefix ($)
            prefixes_list = ["$"]

        prefixes = await Accessory.get(guild)

        prefixes.prefixes = prefixes_list

        bot_user = bot.user
        bot_member = guild.get_member(bot.user.id)

        await bot_member.edit(nick=f"{bot_user.name} | {prefixes_list[0]}")

        await prefixes.store()

    @staticmethod
    async def remove(guild):
        async with config.connection.transaction():
            await config.connection.execute(
                "DELETE FROM accessories WHERE guild_id = $1;",
                guild.id
            )

    @staticmethod
    async def ensure_integrity():
        guilds = bot.guilds

        for guild in guilds:
            async with config.connection.transaction():
                record = await config.connection.fetchrow(
                    "SELECT * FROM accessories WHERE guild_id = $1;",
                    guild.id
                )

            if not record:
                await Accessory.set_prefixes(guild)
