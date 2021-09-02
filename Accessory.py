import config

bot = config.bot

connection = config.connection


# rename "prefixes" table to "accessories"

class Accessory:
    def __init__(self, guild_id, prefixes):
        self.guild_id = guild_id
        self.prefixes = prefixes

    @staticmethod
    async def open(guild):
        async with connection.transaction():
            await connection.execute(
                "INSERT INTO accessories VALUES ($1, $2);",
                guild.id,
                ["$"]  # default prefix
            )

    @staticmethod
    async def get(guild):
        async with connection.transaction():
            values = tuple(await connection.fetchrow(
                "SELECT * FROM accessories WHERE guild_id = $1;",
                guild.id
            ).values())

        if not values:
            await Accessory.open(guild)

            async with connection.transaction():
                values = tuple(await connection.fetchrow(
                    "SELECT * FROM accessories WHERE guild_id = $1;",
                    guild.id
                ).values())

        return Accessory(*values)

    async def store(self):
        async with connection.transaction():
            await connection.execute(
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
        async with connection.transaction():
            await connection.execute(
                "DELETE FROM accessories WHERE guild_id = %(guild_id)s;",
                {"guild_id": guild.id}
            )

    @staticmethod
    async def ensure_integrity():
        guilds = bot.guilds

        for guild in guilds:
            async with connection.transaction():
                value = tuple(await connection.fetchrow(
                    "SELECT * FROM accessories WHERE guild_id = %(guild_id)s;",
                    {"guild_id": guild.id}
                ).values())

            if not value:
                await Accessory.set_prefixes(guild)
