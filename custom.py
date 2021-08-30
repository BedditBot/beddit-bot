import discord

import config

bot = config.bot

connection = config.connection


async def get_user_account(user):
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM bank WHERE user_id=%(user_id)s;",
        {"user_id": user.id}
    )

    values = cursor.fetchone()

    if not values:
        await open_user_account(user)

        cursor.execute(
            "SELECT * FROM bank WHERE user_id=%(user_id)s;",
            {"user_id": user.id}
        )

        values = cursor.fetchone()

    cursor.close()

    keys = ("user_id", "balance", "active_bets", "total_bets", "mean_accuracy")

    user_account = dict(zip(keys, values))

    if user_account["mean_accuracy"]:
        user_account["mean_accuracy"] = float(user_account["mean_accuracy"])

    return user_account


def store_user_account(user_account):
    if user_account["balance"] < 0:
        user_account["balance"] = 0

    if user_account["balance"] > 2147483647:
        user_account["balance"] = 2147483647

    cursor = connection.cursor()

    cursor.execute(
        "UPDATE bank "
        "SET balance = %(balance)s, active_bets = %(active_bets)s, "
        "total_bets = %(total_bets)s, "
        "mean_accuracy = %(mean_accuracy)s "
        "WHERE user_id = %(user_id)s;",
        {
            "user_id": user_account["user_id"],
            "balance": user_account["balance"],
            "active_bets": user_account["active_bets"],
            "total_bets": user_account["total_bets"],
            "mean_accuracy": user_account["mean_accuracy"]
        }
    )

    connection.commit()
    cursor.close()


async def open_user_account(user):
    await user.send(
        embed=discord.Embed(
            title="Warning",
            colour=0xffffff,
            description="Gambling addiction can develop from gambling fake "
                        "virtual currency, like in Beddit, and negatively "
                        "affects self-esteem, relationships, physical/mental "
                        "health, school/work performance and social life.\n"
                        "Beddit **does not encourage or promote** any kind of "
                        "**gambling** with real currency, **we discourage "
                        "it**.\nIn case you think you may have developed "
                        "gambling addiction, please seek help from "
                        "[professionals](https://www.ncpgambling.org/5475-2/)."
        )
    )

    cursor = connection.cursor()

    cursor.execute(
        "INSERT INTO bank VALUES (%(user_id)s, %(balance)s, "
        "%(active_bets)s, %(total_bets)s, %(mean_accuracy)s);",
        {
            "user_id": user.id,
            "balance": 250,
            "active_bets": 0,
            "total_bets": 0,
            "mean_accuracy": None
        }
    )

    connection.commit()
    cursor.close()


# checks if an account already exists for a user
def check_user_account(user):
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM bank WHERE user_id=%(user_id)s;",
        {"user_id": user.id}
    )

    user_account = cursor.fetchone()

    cursor.close()

    return bool(user_account)


# clears active bets on every restart (runs in main.py)
def clear_active_bets():
    cursor = connection.cursor()

    cursor.execute(
        "UPDATE bank SET active_bets = 0 WHERE active_bets > 0;"
    )

    connection.commit()
    cursor.close()


def get_guild_prefixes(guild):
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM prefixes WHERE guild_id = %(guild_id)s;",
        {"guild_id": guild.id}
    )

    values = cursor.fetchone()

    if not values:
        open_guild_prefixes(guild)

        cursor.execute(
            "SELECT * FROM prefixes WHERE guild_id = %(guild_id)s;",
            {"guild_id": guild.id}
        )

        values = cursor.fetchone()

    cursor.close()

    keys = ("guild_id", "prefixes")

    guild_prefixes = dict(zip(keys, values))

    return guild_prefixes


def store_guild_prefixes(guild_prefixes):
    cursor = connection.cursor()

    cursor.execute(
        "UPDATE prefixes "
        "SET prefixes = %(prefixes)s "
        "WHERE guild_id = %(guild_id)s;",
        {
            "guild_id": guild_prefixes["guild_id"],
            "prefixes": guild_prefixes["prefixes"]
        }
    )

    connection.commit()
    cursor.close()


def open_guild_prefixes(guild):
    cursor = connection.cursor()

    cursor.execute(
        "INSERT INTO prefixes VALUES (%(guild_id)s, %(prefixes)s);",
        {
            "guild_id": guild.id,
            "prefixes": ["$"]  # default prefix
        }
    )

    connection.commit()
    cursor.close()


async def set_guild_prefixes(guild, prefixes=None):
    if not prefixes:
        # sets default prefix ($)
        prefixes = ["$"]

    guild_prefixes = get_guild_prefixes(guild)

    guild_prefixes["prefixes"] = prefixes

    bot_user = bot.user
    bot_member = guild.get_member(bot.user.id)

    await bot_member.edit(nick=f"{bot_user.name} | {prefixes[0]}")

    store_guild_prefixes(guild_prefixes)


def remove_guild_prefixes(guild):
    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM prefixes WHERE guild_id = %(guild_id)s;",
        {"guild_id": guild.id}
    )

    connection.commit()
    cursor.close()


async def ensure_prefixes_integrity():
    cursor = connection.cursor()

    guilds = bot.guilds

    for guild in guilds:
        cursor.execute(
            "SELECT * FROM prefixes WHERE guild_id = %(guild_id)s;",
            {"guild_id": guild.id}
        )

        if not cursor.fetchone():
            await set_guild_prefixes(guild)

    cursor.close()


def disconnect_database():
    connection.close()


# argument user_attr (user attribute) is something related to the user
# like ID, name or name with discriminator
def find_user(ctx, user_attr):
    user = None

    def not_mention(text):
        return text.replace("<@", "").replace(">", "").replace("!", "")

    not_mention_user_attr = not_mention(user_attr)

    # checks if user_attr is an ID
    if not_mention_user_attr.isdigit() and len(not_mention_user_attr) >= 17:
        user = bot.get_user(int(not_mention_user_attr))

    # checks if user_attr is a name with discriminator (tag)
    elif "#" in user_attr:
        for member in ctx.guild.members:
            if str(member) == user_attr:
                user = member

                break
    else:
        potential_users = []

        for member in ctx.guild.members:

            # looks for user with the same lower case name
            if member.name.lower() == user_attr.lower():
                potential_users.append(member)

        if len(potential_users) == 1:
            user = potential_users[0]
        elif not potential_users:
            pass
        else:
            potential_users.clear()

            for member in ctx.guild.members:

                # looks for user with the same name
                if member.name == user_attr:
                    potential_users.append(member)

            if len(potential_users) == 1:
                user = potential_users[0]
            else:
                pass

    return user


# ini_amount is the initial amount of accuracies used for ini_mean
def calculate_mean_accuracy(ini_mean, ini_amount, new_accuracy):
    if not ini_mean:
        ini_mean = 0

    fin_amount = ini_amount + 1

    fin_mean = (ini_mean * ini_amount + new_accuracy) / fin_amount

    return round(fin_mean, 3)


def separate_digits(num):
    num_list = list(str(num))
    reversed_final_list = []

    i = 0
    for num in reversed(num_list):
        if (i + 1) % 3 == 0:
            reversed_final_list.append("{}{}".format(u'\u2009', num))
        else:
            reversed_final_list.append(num)

        i += 1

    final_list = reversed(reversed_final_list)

    return "".join(final_list).strip(u'\u2009')
