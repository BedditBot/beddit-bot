import json

import config

bot = config.bot


# bank format: {
#   "[user_id]": {
#       "balance": [number of bedcoins],
#       "active_bets": [number of active bets]
#   },
#   ...
# }


# opens an account if the user does not have one already
def open_account(user):
    bank_data = get_bank_data()

    if str(user.id) in bank_data:
        return

    bank_data[str(user.id)] = {
        "balance": 100,
        "active_bets": 0
    }

    with open("bank.json", "w") as file:
        json.dump(bank_data, file)


def get_bank_data():
    with open("bank.json", "r") as file:
        bank_data = json.load(file)

    return bank_data


def store_bank_data(bank_data):
    for account in tuple(bank_data.items()):
        user_id = account[0]
        values = account[1]

        balance = tuple(values.items())[0][1]

        if balance < 0:
            bank_data[user_id]["balance"] = 0

    with open("bank.json", "w") as file:
        json.dump(bank_data, file)


def find_user(ctx, user):
    def not_mention(text):
        return text.replace("<@", "").replace(">", "").replace("!", "")

    not_mention_user = not_mention(user)
    print(not_mention_user)
    if not_mention_user.isdigit() and len(not_mention_user) == 18:
        user_id = int(not_mention_user)

        user = bot.get_user(user_id)

        if not user:
            return None
    elif user[-5] == "#" and user[-4:].isdigit():
        found = False

        for member in ctx.guild.members:
            if str(member) == user:
                user = member

                found = True

                break

        if not found:
            return None
    else:
        potential_users = []

        for member in ctx.guild.members:
            if member.name.lower() == user.lower():
                potential_users.append(member)

        if len(potential_users) == 1:
            user = potential_users[0]
        elif not potential_users:
            return None
        else:
            potential_users.clear()

            for member in ctx.guild.members:
                if member.name == user:
                    potential_users.append(member)

            if len(potential_users) == 1:
                user = potential_users[0]
            elif not potential_users:
                return None
            else:
                return None

    return user
