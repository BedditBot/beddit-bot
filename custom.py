from sys import exit as sys_exit

import config

bot = config.bot


# clears active bets on every restart (runs in main.py)
async def clear_active_bets():
    async with config.connection.transaction():
        await config.connection.execute(
            "UPDATE accounts SET active_bets = 0 WHERE active_bets > 0;"
        )


async def disconnect_database():
    await config.connection.close()


async def terminate(_, __):
    print("Terminating...")

    await bot.logout()

    await disconnect_database()

    sys_exit()


# argument user_attr (user attribute) is something related to the user
# like ID, name or name with discriminator
async def find_user(ctx, user_attr):
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
