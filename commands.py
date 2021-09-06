import sys

import asyncpraw
import random
from discord.ext import commands
import datetime
import math

# import custom
from custom import *
from Account import Account
from Accessory import Accessory

bot = config.bot

reddit_client = asyncpraw.Reddit(
    client_id=config.R_CLIENT_ID,
    client_secret=config.R_CLIENT_SECRET,
    username=config.R_USERNAME,
    password=config.R_PASSWORD,
    user_agent=config.R_USER_AGENT
)

gold_emote = " <:gold:884085535965065266>"
platinum_emote = " <:platinum:884147435709030440>"


@bot.command(
    aliases=["latency"],
    help="Used for getting the bot's ping.",
    hidden=True
)
async def ping(ctx):
    if not await bot.is_owner(ctx.author):
        return

    latency = round(bot.latency, 3) * 1000  # in ms to 3 d.p.

    await ctx.send(f"Pong! ({latency}ms)")


# closes the bot (only bot owners)
@bot.command(
    help="Used for restarting the bot.",
    hidden=True
)
async def cease(ctx):
    if not await bot.is_owner(ctx.author):
        return

    await ctx.send("Farewell...")

    # await custom.terminate()

    sys.exit()


def get_help_pages(dev):
    commands_list = []

    for command in bot.commands:
        if not dev:
            if not command.hidden:
                commands_list.append(command)
        else:
            if command.hidden:
                commands_list.append(command)

    commands_list.sort(key=lambda command_in: command_in.name)

    grouped_commands_list = [
        commands_list[i:i + 10] for i in range(0, len(commands_list), 10)
    ]

    pages = []

    i = 0
    total_pages = len(grouped_commands_list)

    for group in grouped_commands_list:
        page = discord.Embed(
            title=f"Commands",
            color=0xff4500  # orangered
        ).set_footer(
            text=f"Showing page {i + 1} of {total_pages}, "
                 f"use reactions to switch pages."
        )

        for command in group:
            page.add_field(
                name=command.name,
                value=(
                        command.help +
                        (
                            f"\n*Usage:* `{command.usage}`" if command.usage
                            else ""
                        ) +
                        (
                            f"\n*Alias"
                            f"{'' if len(command.aliases) == 1 else 'es'}"
                            f":* `{'`, `'.join(command.aliases)}`"
                            if command.aliases
                            else ""
                        )
                ),
                inline=False
            )

        pages.append(page)

        i += 1

    return pages


bot.remove_command("help")


@bot.command(
    name="help",
    aliases=["h"],
    help="Used for getting this message."
)
@commands.cooldown(1, 5, type=commands.BucketType.user)
@commands.max_concurrency(1, per=commands.BucketType.user)
async def help_(ctx):
    pages = help_pages
    total_pages = len(pages)

    n = 0

    help_message = await ctx.send(embed=pages[n])

    react_emotes = ("◀️", "❌", "▶️")

    for react_emote in react_emotes:
        await help_message.add_reaction(react_emote)

    def check(reaction_in, user_in):
        return (
                user_in == ctx.author and str(reaction_in) in react_emotes and
                reaction_in.message == help_message
        )

    while True:
        try:
            reaction, user = await bot.wait_for(
                "reaction_add",
                check=check,
                timeout=60
            )

            if str(reaction) == "▶️":
                if n + 2 > total_pages:
                    pass
                else:
                    n += 1

                    await help_message.edit(embed=pages[n])

                try:
                    await help_message.remove_reaction(reaction, user)
                except discord.errors.Forbidden:
                    pass
            elif str(reaction) == "◀️":
                if n == 0:
                    pass
                else:
                    n -= 1

                    await help_message.edit(embed=pages[n])

                try:
                    await help_message.remove_reaction(reaction, user)
                except discord.errors.Forbidden:
                    pass
            else:
                try:
                    await help_message.clear_reactions()
                except discord.errors.Forbidden:
                    pass

                break
        except asyncio.TimeoutError:
            try:
                await help_message.clear_reactions()
            except discord.errors.Forbidden:
                pass

            break


@bot.command(
    name="devhelp",
    aliases=["dh"],
    help="Used for getting this message.",
    hidden=True
)
@commands.cooldown(1, 5, type=commands.BucketType.user)
@commands.max_concurrency(1, per=commands.BucketType.user)
async def developer_help(ctx):
    if not await bot.is_owner(ctx.author):
        return

    pages = dev_help_pages
    total_pages = len(pages)

    n = 0

    help_message = await ctx.send(embed=pages[n])

    react_emotes = ("◀️", "❌", "▶️")

    for react_emote in react_emotes:
        await help_message.add_reaction(react_emote)

    def check(reaction_in, user_in):
        return (
                user_in == ctx.author and str(reaction_in) in react_emotes and
                reaction_in.message == help_message
        )

    while True:
        try:
            reaction, user = await bot.wait_for(
                "reaction_add",
                check=check,
                timeout=60
            )

            if str(reaction) == "▶️":
                if n + 2 > total_pages:
                    pass
                else:
                    n += 1

                    await help_message.edit(embed=pages[n])

                try:
                    await help_message.remove_reaction(reaction, user)
                except discord.errors.Forbidden:
                    pass
            elif str(reaction) == "◀️":
                if n == 0:
                    pass
                else:
                    n -= 1

                    await help_message.edit(embed=pages[n])

                try:
                    await help_message.remove_reaction(reaction, user)
                except discord.errors.Forbidden:
                    pass
            else:
                try:
                    await help_message.clear_reactions()
                except discord.errors.Forbidden:
                    pass

                break
        except asyncio.TimeoutError:
            try:
                await help_message.clear_reactions()
            except discord.errors.Forbidden:
                pass

            break


@bot.command(
    aliases=["information"],
    help="Used for getting information about the bot."
)
async def info(ctx):
    developers = []

    app_info = await bot.application_info()

    for owner in app_info.team.members:
        developers.append(f"`{str(owner)}`")

    developers.sort()
    developers_string = "\n".join(developers)

    await ctx.send(
        embed=discord.Embed(
            title="Information",
            color=0xff4500  # orangered
        ).add_field(
            name="GitHub repository",
            value="http://github.bedditbot.eu",
            inline=False
        ).add_field(
            name="Discord server",
            value="https://discord.gg/HjT3YpU",
            inline=False
        ).add_field(
            name="Bot invite",
            value="http://invite.bedditbot.eu",
            inline=False
        ).add_field(
            name="Developers",
            value=developers_string,
            inline=False
        )
    )


@bot.command(
    name="postinfo",
    aliases=["pi", "pinfo"],
    help="Used for getting information (number of upvotes and "
         "downvotes) about a Reddit post."
)
async def post_information(ctx, link):
    post = await reddit_client.submission(url=link)

    score = post.score
    ratio = post.upvote_ratio

    upvotes = round(
        (ratio * score) / (2 * ratio - 1)
    )

    downvotes = round(
        (score * (1 - ratio)) / (2 * ratio - 1)
    )

    timedelta = (
            datetime.datetime.utcnow() -
            datetime.datetime.utcfromtimestamp(post.created_utc)
    )

    def express_time(time):
        days = time.days
        hours = math.floor(time.seconds / 3600)
        minutes = math.floor(time.seconds % 3600 / 60)
        seconds = time.seconds % 60

        if days != 0:
            return (
                f"{days} {'days' if days != 1 else 'day'} "
                f"{hours} {'hours' if hours != 1 else 'hour'} "
                f"{minutes} {'minutes' if minutes != 1 else 'minute'} "
                f"ago"
            )
        else:
            return (
                f"{hours} {'hours' if hours != 1 else 'hour'} "
                f"{minutes} {'minutes' if minutes != 1 else 'minute'} "
                f"{seconds} {'seconds' if seconds != 1 else 'second'} "
                f"ago"
            )

    await ctx.send(
        embed=discord.Embed(
            title="Post information",
            url=link,
            colour=0xff4500  # orangered
        ).add_field(
            name="Title",
            value=post.title,
            inline=False
        ).add_field(
            name="Created",
            value=express_time(timedelta),
            inline=False
        ).add_field(
            name="Score",
            value=separate_digits(score),
            inline=False
        ).add_field(
            name="Upvotes",
            value=separate_digits(upvotes),
            inline=False
        ).add_field(
            name="Downvotes",
            value=separate_digits(downvotes),
            inline=False
        ).add_field(
            name="Comments",
            value=separate_digits(post.num_comments),
            inline=False
        )
    )


@bot.command(
    name="balance",
    aliases=["bal"],
    help=f"Used for getting the gold{gold_emote} "
         "balance of a user."
)
async def balance_(ctx, user_attr=None):
    if not user_attr:
        user = ctx.author
    else:
        user = find_user(ctx, user_attr)
        if not user:
            return

    account = await Account.get(user)

    await ctx.send(
        embed=discord.Embed(
            title="Balance",
            color=0xffd700  # gold
        ).add_field(
            name="Gold",
            value=f"{separate_digits(account.gold)}{gold_emote}",
            inline=False
        ).add_field(
            name="Platinum",
            value=f"{separate_digits(account.platinum)}{platinum_emote}",
            inline=False
        ).set_thumbnail(
            url="https://static.wikia.nocookie.net/reddit/images/1/10/Gold.png"
                "/revision/latest/scale-to-width-down/512?cb=20200815001830"
        ).set_footer(
            text=str(user),
            icon_url=str(user.avatar_url)
        )
    )


# @bot.command(
#     name="editaccount",
#     aliases=["ea"],
#     help="Used for manually editing account information.",
#     hidden=True
# )
# async def edit_account(ctx, user_attr, field, value):
#     if not await bot.is_owner(ctx.author):
#         return
#
#     if not user_attr:
#         user = ctx.author
#     else:
#         user = find_user(ctx, user_attr)
#         if not user:
#             await ctx.send("This user wasn't found!")
#
#             return
#
#     account = await Account.get(user)
#
#     if field not in account:
#         await ctx.send("Field not found.")
#
#         return
#
#     if not value.replace(".", "").isdigit() and value != "None":
#         await ctx.send("Invalid value.")
#
#         return
#
#     if "." in value:
#         value = round(float(value), 3)
#     elif value == "None":
#         value = None
#     else:
#         value = int(value)
#
#     account[field] = value
#
#     await store_user_account(account)
#
#     await ctx.send(
#         f"Edited {str(user)}'s bank account {field} field to {value}!"
#     )


@bot.command(
    pass_context=True,
    help="Used for collecting your daily reward."
)
@commands.cooldown(1, 60 * 60 * 24, commands.BucketType.user)
async def daily(ctx):
    user = ctx.author

    account = await Account.get(user)

    account.gold += 100

    await account.store()

    await ctx.send(
        embed=discord.Embed(
            title="Balance (+Daily reward)",
            color=0xffd700  # gold
        ).add_field(
            name="Gold",
            value=(separate_digits(account.gold) + " (+100)"),
            inline=False
        ).add_field(
            name="Platinum",
            value=separate_digits(account.platinum),
            inline=False
        ).set_thumbnail(
            url="https://i.imgur.com/9aAfwcJ.png"
        ).set_footer(
            text=str(user),
            icon_url=str(user.avatar_url)
        )
    )


TRANSFER_TAX_RATE = 0.05  # 5%


@bot.command(
    help=f"Used for transferring gold{gold_emote} "
         f"to another user (with a {TRANSFER_TAX_RATE * 100}% tax)."
)
async def transfer(ctx, *, args):
    args_list = args.split()

    amount = args_list[-1]
    receiver_attr = " ".join(args_list[:-1])

    sender = ctx.author

    sender_account = await Account.get(sender)

    if sender_account.active_bets > 0:
        await send_error(
            ctx,
            f"Can't transfer gold{gold_emote} between users with active bets."
        )

        return

    if not amount.isdigit():
        return

    amount = int(amount)

    if amount == 0:
        return

    receiver = find_user(ctx, receiver_attr)

    if not receiver:
        return

    if sender == receiver:
        return

    if amount > sender_account.gold:
        return

    receiver_account = await Account.get(receiver)

    if receiver_account.active_bets > 0:
        await send_error(
            ctx,
            f"Can't transfer gold{gold_emote} between users with active bets."
        )

        return

    sender_account.gold -= amount
    receiver_account.gold += int(amount - TRANSFER_TAX_RATE * amount)

    await sender_account.store()
    await receiver_account.store()

    await ctx.send(
        embed=discord.Embed(
            title="Transfer",
            color=0xffd700,  # gold
            description=f"Transferred {amount} "
                        f"gold{gold_emote} "
                        f"from `{str(sender)}` to `{str(receiver)}` "
                        f"with a {round(TRANSFER_TAX_RATE * 100)}% tax rate."
        ).set_footer(
            text=str(sender),
            icon_url=str(sender.avatar_url)
        )
    )


@bot.command(
    help=f"Used to gamble 50 gold{gold_emote}. "
         f"(Try it out and hope for the jackpot!)"
)
@commands.cooldown(1, 1, commands.BucketType.user)
async def gamble(ctx):
    user = ctx.author

    account = await Account.get(user)

    gold = account.gold

    if gold < 50:
        return

    outcome = random.randint(1, 100)

    if outcome <= 25:
        winnings = random.randint(1, 25)
    elif outcome <= 75:
        winnings = random.randint(25, 50)
    elif outcome <= 99:
        winnings = random.randint(50, 100)
    else:
        winnings = 500

    true_winnings = winnings - 50

    account.gold += true_winnings

    await account.store()

    await ctx.send(
        embed=discord.Embed(
            title="Gambling",
            color=0x39ff14,  # neon green
            description=f"Gambled 50 gold{gold_emote} "
                        f"and won {winnings} "
                        f"gold{gold_emote}."
        ).set_footer(
            text=str(user),
            icon_url=str(user.avatar_url)
        )
    )


hidden_balance_tracker = dict()


@bot.command(
    name="convert",
    aliases=["con", "c"],
    help=f"Used for converting gold{gold_emote} to platinum{platinum_emote}."
)
@commands.cooldown(1, 30, commands.BucketType.user)
async def convert_(ctx):
    user = ctx.author

    account = await Account.get(user)

    gold = account.gold
    platinum = account.platinum

    price_1 = platinum ** 3
    price_2 = 2 * price_1
    price_3 = 3 * price_1

    message = await ctx.send(
        embed=discord.Embed(
            title="Platinum Conversion",
            description=f"React to convert gold{gold_emote} to "
                        f"platinum{platinum_emote}.",
            color=0xe5e4e2  # platinum
        ).add_field(
            name="Option 1️⃣",
            value=f"{separate_digits(price_1)}{gold_emote} to "
                  f"1{platinum_emote}",
            inline=False
        ).add_field(
            name="Option 2️⃣",
            value=f"{separate_digits(price_2)}{gold_emote} to "
                  f"2{platinum_emote}",
            inline=False
        ).add_field(
            name="Option 3️⃣",
            value=f"{separate_digits(price_3)}{gold_emote} to "
                  f"3{platinum_emote}",
            inline=False
        ).set_footer(
            text=str(user),
            icon_url=str(user.avatar_url)
        ).set_thumbnail(
            url="https://static.wikia.nocookie.net/reddit/images/a/ac/"
                "Platinum.png/revision/latest/scale-to-width-down/512"
                "?cb=20200815001756"
        )
    )

    await message.add_reaction("1️⃣")
    await message.add_reaction("2️⃣")
    await message.add_reaction("3️⃣")

    async def update(price, amount):
        nonlocal account, gold, platinum, price_1, price_2, price_3

        account = await Account.get(user)

        gold = account.gold
        platinum = account.platinum

        price_1 = platinum ** 3
        price_2 = 2 * price_1
        price_3 = 3 * price_1

        await message.edit(
            embed=discord.Embed(
                title="Platinum Conversion",
                description=f"Converted {price}{gold_emote} to "
                            f"{amount}{platinum_emote}.",
                color=0xe5e4e2  # platinum
            ).add_field(
                name="Option 1️⃣",
                value=f"{separate_digits(price_1)}{gold_emote} to "
                      f"1{platinum_emote}",
                inline=False
            ).add_field(
                name="Option 2️⃣",
                value=f"{separate_digits(price_2)}{gold_emote} to "
                      f"2{platinum_emote}",
                inline=False
            ).add_field(
                name="Option 3️⃣",
                value=f"{separate_digits(price_3)}{gold_emote} to "
                      f"3{platinum_emote}",
                inline=False
            ).set_footer(
                text=str(user),
                icon_url=str(user.avatar_url)
            ).set_thumbnail(
                url="https://static.wikia.nocookie.net/reddit/images/a/ac/"
                    "Platinum.png/revision/latest/scale-to-width-down/512"
                    "?cb=20200815001756"
            )
        )

    def check(reaction_in, user_in):
        return (
                user_in == ctx.author and str(reaction_in.emoji) in
                ("1️⃣", "2️⃣", "3️⃣") and reaction_in.message == message
        )

    while True:
        try:
            reaction, user = await bot.wait_for(
                "reaction_add",
                check=check,
                timeout=45
            )

            if str(reaction.emoji) == "1️⃣":
                if gold >= price_1:
                    account.gold -= price_1
                    account.platinum += 1

                    await account.store()

                    await update(price_1, 1)
                else:
                    await send_error(
                        ctx,
                        f"Insufficient gold{gold_emote} for conversion."
                    )

                    return
            elif str(reaction.emoji) == "2️⃣":
                if gold >= price_2:
                    account.gold -= price_2
                    account.platinum += 2

                    await account.store()

                    await update(price_2, 2)
                else:
                    await send_error(
                        ctx,
                        f"Insufficient gold{gold_emote} for conversion."
                    )

                    return
            elif str(reaction.emoji) == "3️⃣":
                if gold >= price_3:
                    account.gold -= price_3
                    account.platinum += 3

                    await account.store()

                    await update(price_3, 3)
                else:
                    await send_error(
                        ctx,
                        f"Insufficient gold{gold_emote} for conversion."
                    )

                    return
            try:
                await message.remove_reaction(reaction, user)
            except discord.errors.Forbidden:
                pass
        except asyncio.TimeoutError:
            try:
                await message.clear_reactions()
            except discord.errors.Forbidden:
                pass

            break


@bot.command(
    help=f"Used to bet on Reddit posts. *Use as [Reddit post URL] "
         f"[bet amount (in gold{gold_emote})] "
         f"[time (in s/m/h)] "
         f"[predicted upvotes on that post after that time].*"
)
@commands.cooldown(1, 5, commands.BucketType.user)
async def bet(ctx, link, amount, time, predicted_ups):
    user = ctx.author

    if not amount.rstrip("%").isdigit() or not predicted_ups.isdigit():
        await ctx.send("You can't bet that!")

        return

    account = await Account.get(user)

    if "%" in amount:
        if not 0 < float(amount.rstrip("%")) <= 100:
            await ctx.send("You can't bet that!")

            return

        amount = int(
            float(amount.rstrip("%")) * account.gold / 100
        )
    else:
        amount = int(amount)

    predicted_ups = int(predicted_ups)
    initial_post = await reddit_client.submission(url=link)

    age = int(
        datetime.datetime.utcnow().timestamp() - initial_post.created_utc
    )

    if age > 86400:
        await ctx.send("You can't bet on posts older than 24 hours!")

        return

    if initial_post.archived or initial_post.locked:
        await ctx.send("You can't bet on archived or locked posts!")

        return

    # if not ctx.channel.is_nsfw() and initial_post.nsfw:
    #     await ctx.send("You can't bet on NSFW posts here!")
    #
    #     return

    initial_ups = initial_post.ups

    if predicted_ups <= initial_ups + 1:
        await ctx.send(
            "Your predicted upvotes can't be lower than or equal to "
            "the current amount of upvotes (plus 1)!"
        )

        return

    if account.gold < amount:
        await ctx.send("You do not have enough chips to bet this much!")

        return

    if account.active_bets >= 3:
        await ctx.send("You already have 3 bets running!")

        return

    # gets time unit, then removes it and converts time to seconds
    if "s" in time:
        time_in_seconds = time.rstrip("s")

        if not time_in_seconds.isdigit():
            await ctx.send("You can't use that as time!")

            return

        time_in_seconds = int(time_in_seconds)

    elif "m" in time:
        time_in_seconds = time.rstrip("m")

        if not time_in_seconds.isdigit():
            await ctx.send("You can't use that as time!")

            return

        time_in_seconds = int(time_in_seconds) * 60
    elif "h" in time:
        time_in_seconds = time.rstrip("h")

        if not time_in_seconds.isdigit():
            await ctx.send("You can't use that as time!")

            return

        time_in_seconds = int(time_in_seconds) * 3600
    elif time.isdigit():
        await ctx.send("Please specify a time unit.")

        return
    else:
        await ctx.send("You can't use that as time!")

        return

    predicted_ups_difference = predicted_ups - initial_ups

    # sends initial message with specifics
    await ctx.send(
        f"This post has {separate_digits(initial_ups)} "
        f"upvotes right now! "
        f"You bet {separate_digits(amount)} "
        f"gold{gold_emote} on it reaching "
        f"{separate_digits(predicted_ups)} upvotes in {time}!"
    )

    account.active_bets += 1
    account.gold -= amount

    try:
        hidden_balance_tracker[user.id] += amount
    except KeyError:
        hidden_balance_tracker[user.id] = 0
        hidden_balance_tracker[user.id] += amount

    await account.store()

    # waits until the chosen time runs out, then calculates the accuracy
    await asyncio.sleep(time_in_seconds)

    final_post = await reddit_client.submission(url=link)
    final_ups = final_post.ups

    # pct means percent
    try:
        if predicted_ups > final_ups:
            accuracy = abs(final_ups / predicted_ups)
        else:
            accuracy = abs(predicted_ups / final_ups)
    except ZeroDivisionError:
        await ctx.send("Oops! Something went wrong.")

        return

    accuracy = round(accuracy, 3)
    accuracy_in_pct = accuracy * 100

    account = await Account.get(user)

    true_balance = account.gold + hidden_balance_tracker[user.id]

    # multiplier formula
    multiplier = (
            (625 / 676) * math.exp(- true_balance / (10_000_000 / math.log(2)))
            * (accuracy - 0.4) ** 3 * time_in_seconds ** (2 / 7) *
            math.log(predicted_ups_difference, 15)
    )

    winnings = int(amount * multiplier)
    true_winnings = winnings - amount

    account.gold += winnings

    hidden_balance_tracker[user.id] -= amount

    if account.gold >= 2147483647:
        await ctx.send(
            f"Hello {user.mention}! Great job! You have hit the limits of "
            f"time and space! (Or possibly our programming...)"
        )

        account.gold -= winnings
        account.active_bets -= 1
        account.gold += amount

        await account.store()

        return

    account.active_bets -= 1
    account.mean_accuracy = calculate_mean_accuracy(
        account.mean_accuracy,
        account.total_bets,
        accuracy
    )
    account.total_bets += 1

    await account.store()

    if true_winnings > 0:
        await ctx.send(
            f"Hello {user.mention}! It's {time} later, and the post has "
            f"{separate_digits(final_ups)} upvotes right now! "
            f"You were {accuracy_in_pct}% "
            f"accurate and won {separate_digits(true_winnings)} "
            f"gold{gold_emote}!"
        )
    elif true_winnings == 0:
        await ctx.send(
            f"Hello {user.mention}! It's {time} later, and the post has "
            f"{separate_digits(final_ups)} upvotes right now! "
            f"You were {accuracy_in_pct}% "
            f"accurate but won nothing."
        )
    else:
        await ctx.send(
            f"Hello {user.mention}! It's {time} later, and the post has "
            f"{separate_digits(final_ups)} upvotes right now! "
            f"You were {accuracy_in_pct}% "
            f"accurate and lost {separate_digits(abs(true_winnings))} "
            f"gold{gold_emote}!"
        )


@bot.command(
    name="activebets",
    aliases=["bets"],
    help="Used for getting the active bets of a user."
)
async def active_bets_(ctx, user_attr=None):
    if not user_attr:
        user = ctx.author
    else:
        user = find_user(ctx, user_attr)

        if not user:
            return

    account = await Account.get(user)

    active_bets = account.active_bets

    await ctx.send(
        embed=discord.Embed(
            title="Active bets",
            color=0xff4500,  # orangered
            description=active_bets
        ).set_footer(
            text=str(user),
            icon_url=str(user.avatar_url)
        )
    )


@bot.command(
    aliases=["statistics"],
    help="Used for getting someone's betting statistics."
)
async def stats(ctx, user_attr=None):
    if not user_attr:
        user = ctx.author
    else:
        user = find_user(ctx, user_attr)

        if not user:
            return

    account = await Account.get(user)

    mean_accuracy = account.mean_accuracy
    total_bets = account.total_bets

    await ctx.send(
        embed=discord.Embed(
            title="Statistics",
            color=0x4000ff  # ultramarine
        ).set_thumbnail(
            url="https://imgur.com/UpdCchY.png"
        ).add_field(
            name="Mean accuracy",
            value=(
                f"{round(mean_accuracy * 100, 1)}%" if mean_accuracy else "NaN"
            ),
            inline=False
        ).add_field(
            name="Total bets",
            value=separate_digits(total_bets),
            inline=False
        ).set_footer(
            text=str(user),
            icon_url=str(user.avatar_url)
        )
    )


@bot.command(
    name="factors",
    alieases=["facs"],
    help="Used for getting someone's bet winnings factors."
)
async def factors_(ctx, user_attr=None):
    if not user_attr:
        user = ctx.author
    else:
        user = find_user(ctx, user_attr)

        if not user:
            return

    account = await Account.get(user)

    try:
        hidden_balance_tracker[user.id]
    except KeyError:
        hidden_balance_tracker[user.id] = 0

    true_balance = account.gold + hidden_balance_tracker[user.id]

    await ctx.send(
        embed=discord.Embed(
            title="Factors",
            color=0xff7518  # pumpkin
        ).add_field(
            name="Gold factor",
            value=str(
                round(
                    math.exp(
                        - true_balance / (10_000_000 / math.log(2))) * 100, 1
                )
            ) + "%",
            inline=False
        ).set_footer(
            text=str(user),
            icon_url=str(user.avatar_url)
        )
    )


@bot.command(
    name="leaderboard",
    aliases=["lb"],
    help="Used for getting the leaderboards for this server.",
    usage="leaderboard [balance/accuracy]"
)
async def leaderboard_(ctx, category="gold", size=10):
    if category in "accuracy":
        category = "a"
    else:
        category = "g"

    if size <= 0:
        size = 10

    guild = ctx.guild

    accounts = []

    for member in guild.members:
        user = bot.get_user(member.id)

        if await Account.check(user):
            account = await Account.get(user)

            accounts.append(account)

    # leaderboard is just sorted collection
    collection = {}
    leaderboard = {}

    if category == "a":
        for account in accounts:
            mean_accuracy = account.mean_accuracy

            if mean_accuracy:
                collection[account.user_id] = mean_accuracy
    else:
        for account in accounts:
            gold = account.gold

            collection[account.user_id] = gold

    for user_id in sorted(collection, key=collection.get, reverse=True):
        leaderboard[user_id] = collection[user_id]

    if category == "a":
        embed = discord.Embed(
            title=f"Mean Accuracy Leaderboard of {str(guild)}",
            description="*Not on this leaderboard? Go bet on some posts!*",
            color=0x4000ff  # ultramarine

        )
    else:
        embed = discord.Embed(
            title=f"Gold Leaderboard of {str(guild)}",
            description="*Not on this leaderboard? Go bet on some posts!*",
            color=0xffd700  # gold
        )

    # for medal emotes
    def determine_medal(ranking):
        if ranking == 1:
            return ":first_place:"
        elif ranking == 2:
            return ":second_place:"
        elif ranking == 3:
            return ":third_place:"
        else:
            return ":medal:"

    i = 1

    if category == "a":
        for user_id in leaderboard:
            user = bot.get_user(user_id)

            account = await Account.get(user)

            embed.add_field(
                name=f"{determine_medal(i)} {str(user)}",
                value=f"{round(leaderboard[user_id] * 100, 1)}% "
                      f"("
                      f"Total bets: "
                      f"{separate_digits(account.total_bets)}"
                      f")",
                inline=False
            )

            if i == size:
                break
            else:
                i += 1
    else:
        for user_id in leaderboard:
            user = bot.get_user(user_id)

            embed.add_field(
                name=f"{determine_medal(i)} {str(user)}",
                value=f"{separate_digits(leaderboard[user_id])} "
                      f"gold{gold_emote}",
                inline=False
            )

            if i == size:
                break
            else:
                i += 1

    await ctx.send(embed=embed)


@bot.command(
    name="prefixes",
    aliases=["prefix"],
    help="Used for getting the bot's server prefixes."
)
async def prefix_(ctx):
    accessory = await Accessory.get(ctx.guild)

    prefixes = accessory.prefixes

    await ctx.send(
        embed=discord.Embed(
            title=f"Prefixes of {str(ctx.guild)}",
            color=0xff4500,  # orangered
            description=f"`{'`/`'.join(prefixes)}`"
        )
    )


@bot.command(
    name="setprefixes",
    aliases=["setprefix", "changeprefix", "changeprefixes"],
    help="Used for changing the bot's server prefixes. "
         "(Only works if the user has the Administrator permission.)"
)
@commands.has_permissions(administrator=True)
async def set_prefix(ctx, *, args):
    prefixes = list(dict.fromkeys(args.split()))  # removes duplicates

    if len(prefixes) > 1:
        for prefix in prefixes:
            for char in prefix:
                for other_prefix in [
                    other_prefix for other_prefix in prefixes
                    if other_prefix != prefix
                ]:
                    if char in other_prefix:
                        await ctx.send("You can't use that as prefix!")

                        return

    await Accessory.set_prefixes(ctx.guild, prefixes)

    await ctx.send(
        f"You have changed the server "
        f"{'prefix' if len(prefixes) == 1 else 'prefixes'} to "
        f"'{', '.join(prefixes)}'!"
    )


help_pages = get_help_pages(False)
dev_help_pages = get_help_pages(True)
