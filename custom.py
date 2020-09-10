import json

import config

bot = config.bot


def get_prefixes():
    with open("prefixes.json", "r") as file:
        file_prefixes = json.load(file)

    prefixes = {}

    for guild_id in file_prefixes:
        prefixes[int(guild_id)] = file_prefixes[guild_id]

    return prefixes


def store_prefixes(prefixes):
    file_prefixes = {}

    for guild_id in prefixes:
        file_prefixes[str(guild_id)] = prefixes[guild_id]

    with open("prefixes.json", "w") as file:
        json.dump(file_prefixes, file, indent=4)


def set_guild_prefixes(guild, prefixes=None):
    prefixes_data = get_prefixes()

    if not prefixes:
        # sets default prefix ($)
        prefixes_data[guild.id] = "$"
    else:
        prefixes_data[guild.id] = prefixes

    store_prefixes(prefixes_data)


def remove_guild_prefixes(guild):
    prefixes = get_prefixes()

    prefixes.pop(guild.id)

    store_prefixes(prefixes)


def ensure_prefixes_integrity():
    guilds = bot.guilds

    prefixes = get_prefixes()

    for guild in guilds:
        if guild.id not in prefixes:
            set_guild_prefixes(guild)


# bank format: {
#   "[user_id]": {
#       "balance": [number of bedcoins],
#       "active_bets": [number of active bets]
#   },
#   ...
# }


# clears active bets on every restart (runs in main.py)
def clear_active_bets():
    bank_data = get_bank_data()

    for user in bank_data:
        bank_data[user]["active_bets"] = 0

    store_bank_data(bank_data)


def get_bank_data():
    with open("bank.json", "r") as file:
        file_bank_data = json.load(file)

    bank_data = {}

    for user_id in file_bank_data:
        bank_data[int(user_id)] = file_bank_data[user_id]

    return bank_data


def store_bank_data(bank_data):
    for user_id in bank_data:
        balance = bank_data[user_id]["balance"]

        if balance < 0:
            bank_data[user_id]["balance"] = 0

    file_bank_data = {}

    for user_id in bank_data:
        file_bank_data[str(user_id)] = bank_data[user_id]

    with open("bank.json", "w") as file:
        json.dump(file_bank_data, file, indent=4)


# opens an account if the user does not have one already
def open_account(user):
    bank_data = get_bank_data()

    if user.id in bank_data:
        return

    bank_data[user.id] = {
        "balance": 100,
        "active_bets": 0,
        "total_bets": 0,
        "mean_accuracy": None
    }

    store_bank_data(bank_data)


# argument user_attr (user attribute) is something related to the user
# like ID, name or name with discriminator
def find_user(ctx, user_attr):
    user = None

    def not_mention(text):
        return text.replace("<@", "").replace(">", "").replace("!", "")

    not_mention_user_attr = not_mention(user_attr)

    # checks if user_attr is an ID
    if not_mention_user_attr.isdigit() and len(not_mention_user_attr) == 18:
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
