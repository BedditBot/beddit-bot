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
        cursor = connection.cursor()

        cursor.execute(
            "INSERT INTO accessories VALUES (%(guild_id)s, %(prefixes)s);",
            {
                "guild_id": guild.id,
                "prefixes": ["$"]  # default prefix
            }
        )

        connection.commit()
        cursor.close()

    @staticmethod
    async def get(guild):
        cursor = connection.cursor()

        cursor.execute(
            "SELECT * FROM accessories WHERE guild_id = %(guild_id)s;",
            {"guild_id": guild.id}
        )

        values = cursor.fetchone()

        if not values:
            await Accessory.open(guild)

            cursor.execute(
                "SELECT * FROM accessories WHERE guild_id = %(guild_id)s;",
                {"guild_id": guild.id}
            )

            values = cursor.fetchone()

        cursor.close()

        return Accessory(*values)

    async def store(self):
        cursor = connection.cursor()

        cursor.execute(
            "UPDATE accessories "
            "SET prefixes = %(prefixes)s "
            "WHERE guild_id = %(guild_id)s;",
            {
                "guild_id": self.guild_id,
                "prefixes": self.prefixes
            }
        )

        connection.commit()
        cursor.close()

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
        cursor = connection.cursor()

        cursor.execute(
            "DELETE FROM accessories WHERE guild_id = %(guild_id)s;",
            {"guild_id": guild.id}
        )

        connection.commit()
        cursor.close()

    @staticmethod
    async def ensure_integrity():
        cursor = connection.cursor()

        guilds = bot.guilds

        for guild in guilds:
            cursor.execute(
                "SELECT * FROM accessories WHERE guild_id = %(guild_id)s;",
                {"guild_id": guild.id}
            )

            if not cursor.fetchone():
                await Accessory.set_prefixes(guild)

        cursor.close()
