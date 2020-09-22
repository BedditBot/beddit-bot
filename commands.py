import sys

import praw
import asyncio
import discord
import random
from discord.ext import commands
import datetime
import math

from custom import *

bot = config.bot

reddit_client = praw.Reddit(
    client_id=config.R_CLIENT_ID,
    client_secret=config.R_CLIENT_SECRET,
    username=config.R_USERNAME,
    password=config.R_PASSWORD,
    user_agent=config.R_USER_AGENT
)


@bot.command(aliases=["latency"])
async def ping(ctx):
    latency = round(bot.latency, 3) * 1000  # in ms to 3 d.p.

    await ctx.send(f"Pong! ({latency}ms)")


# closes the bot (only bot owners)
@bot.command(hidden=True)
async def cease(ctx):
    if not await bot.is_owner(ctx.author):
        return

    disconnect_database()

    await ctx.send("Farewell...")
    print("Done.")

    await bot.close()
    sys.exit()


bot.remove_command("help")


@bot.command(aliases=["help"])
async def help_(ctx):
    first_page_embed = discord.Embed(
        title=f"Commands",
        description=f"*Showing page 1 of 2, use reactions to switch pages.*",
        color=0x009e60  # shamrock green
    ).add_field(
        name="ping",
        value="Used for getting the bot's ping.",
        inline=False
    ).add_field(
        name="prefixes",
        value="Used for getting the bot's server prefixes.",
        inline=False
    ).add_field(
        name="setprefixes",
        value="Used for changing the bot's server prefixes. "
              "(Only works if the user has the Administrator permission.)",
        inline=False
    ).add_field(
        name="help",
        value="Used for getting this message.",
        inline=False
    ).add_field(
        name="balance",
        value="Used for getting the Gold<:MessageGold:755792715257479229> "
              "balance of a user.",
        inline=False
    ).add_field(
        name="transfer",
        value="Used for transferring Gold<:MessageGold:755792715257479229> "
              "to another user (with a 5% tax).",
        inline=False
    ).add_field(
        name="daily",
        value="Used for collecting your daily reward.",
        inline=False
    )

    second_page_embed = discord.Embed(
        title=f"Commands",
        description=f"*Showing page 2 of 2, use reactions to switch pages.*",
        color=0x009e60  # shamrock green
    ).add_field(
        name="stats",
        value="Used for getting your betting statistics.",
        inline=False
    ).add_field(
        name="upvotes",
        value="Used for getting the amount of upvotes a Reddit post has.",
        inline=False
    ).add_field(
        name="downvotes",
        value="Used for getting the amount of downvotes a Reddit post has.",
        inline=False
    ).add_field(
        name="gamble",
        value="Used for gambling your Gold<:MessageGold:755792715257479229> "
              "(50% win rate).",
        inline=False
    ).add_field(
        name="bet",
        value="Used to bet on Reddit posts. *(Use as [Reddit post URL] "
              "[bet amount (in Gold<:MessageGold:755792715257479229>)] "
              "[time (in s/m/h)] "
              "[predicted upvotes on that post after that time])*",
        inline=False
    ).add_field(
        name="bets",
        value="Used for getting the active bets of a user.",
        inline=False
    ).add_field(
        name="balancetop",
        value="Used for getting the Gold<:MessageGold:755792715257479229> "
              "balance leaderboard for this server.",
        inline=False
    ).add_field(
        name="accuracytop",
        value="Used for getting the accuracy leaderboard for this server.",
        inline=False
    )

    help_message = await ctx.send(embed=first_page_embed)

    await help_message.add_reaction("◀️")
    await help_message.add_reaction("▶️")

    def check(reaction_in, user_in):
        return user_in == ctx.author and str(reaction_in.emoji) in ("◀️", "▶️")

    while True:
        try:
            reaction, user = await bot.wait_for(
                "reaction_add",
                check=check,
                timeout=60
            )

            if str(reaction.emoji) == "▶️":
                await help_message.edit(embed=second_page_embed)

                await help_message.remove_reaction(reaction, user)
            elif str(reaction.emoji) == "◀️":
                await help_message.edit(embed=first_page_embed)

                await help_message.remove_reaction(reaction, user)
            else:
                await help_message.remove_reaction(reaction, user)
        except asyncio.TimeoutError:
            break


@bot.command(aliases=["information"])
async def info(ctx):
    developers = []

    app_info = await bot.application_info()

    for owner in app_info.team.members:
        developers.append(str(owner))

    developers.sort()
    developers_string = "\n".join(developers)

    embed = discord.Embed(
        title="Information",
        color=0xff2400
    ).add_field(
        name="GitHub repository",
        value="https://github.com/BedditBot/bot",
        inline=False
    ).add_field(
        name="Discord server",
        value="https://discord.gg/HjT3YpU",
        inline=False
    ).add_field(
        name="Bot invite",
        value="https://invite.bedditbot.com",
        inline=False
    ).add_field(
        name="Developers",
        value=developers_string,
        inline=False
    )

    await ctx.send(embed=embed)


@bot.command()
async def upvotes(ctx, link):
    post = reddit_client.submission(url=link)

    await ctx.send(f"This post has {post.ups} upvotes!")


@bot.command()
async def downvotes(ctx, link):
    post = reddit_client.submission(url=link)

    ratio = post.upvote_ratio
    score = post.score

    if ratio != 0.5:
        ups = round((ratio * score) / (2 * ratio - 1))
    else:
        ups = round(score / 2)

    downs = ups - score

    await ctx.send(f"This post has {downs} downvotes!")


@bot.command()
async def repeat(ctx, *, phrase):
    if 'discord.gg' in phrase:
        await ctx.send("Trying to advertise another server, huh?")
    elif '@' in phrase:
        await ctx.send("No pinging!")
    else:
        await ctx.send(phrase)


@bot.command(aliases=["balance", "bal"])
async def balance_(ctx, user_attr=None):
    if not user_attr:
        user = ctx.author
    else:
        user = find_user(ctx, user_attr)
        if not user:
            await ctx.send("This user wasn't found!")

            return

    user_account = get_user_account(user)

    balance = user_account["balance"]

    embed = discord.Embed(
        title=f"{str(user)}'s Balance",
        color=0xffd700  # gold
    ).add_field(
        name="Gold:",
        value=balance
    ).set_thumbnail(
        url="https://i.imgur.com/9aAfwcJ.png"
    )

    await ctx.send(embed=embed)


@bot.command()
@commands.cooldown(1, 5, commands.BucketType.user)
async def gibcash(ctx, user_attr=None):
    if not await bot.is_owner(ctx.author):
        return

    if not user_attr:
        user = ctx.author
    else:
        user = find_user(ctx, user_attr)
        if not user:
            await ctx.send("This user wasn't found!")

            return

    user_account = get_user_account(user)

    user_account["balance"] += 1000

    store_user_account(user_account)

    await ctx.send(
        f"I deposited 1000 Gold<:MessageGold:755792715257479229> "
        f"to {user.name}'s bank account!"
    )


@bot.command(pass_context=True)
@commands.cooldown(1, 60 * 60 * 24, commands.BucketType.user)
async def daily(ctx):
    user_account = get_user_account(ctx.author)

    user_account["balance"] += 100

    store_user_account(user_account)

    await ctx.send(
        "You collected your daily reward of 100 "
        "Gold<:MessageGold:755792715257479229>!"
    )


TRANSFER_TAX_RATE = 0.05  # 5%


@bot.command()
async def transfer(ctx, *, args):
    args_list = args.split()

    amount = args_list[-1]
    receiver_attr = " ".join(args_list[:-1])

    sender = ctx.author

    sender_account = get_user_account(sender)

    if sender_account["active_bets"] > 0:
        await ctx.send(
            "You can't transfer Gold<:MessageGold:755792715257479229> "
            "while you have active bets!"
        )

        return

    if not amount.isdigit():
        await ctx.send(
            "That is not a valid "
            "Gold<:MessageGold:755792715257479229> amount!"
        )

        return
    amount = int(amount)

    if amount == 0:
        await ctx.send(
            "That is not a valid Gold<:MessageGold:755792715257479229> amount!"
        )

        return

    receiver = find_user(ctx, receiver_attr)
    if not receiver:
        await ctx.send("This user wasn't found!")

        return

    if sender == receiver:
        await ctx.send(
            "You can't transfer Gold<:MessageGold:755792715257479229> "
            "to yourself!"
        )

        return

    if amount > sender_account["balance"]:
        await ctx.send(
            "You don't have enough Gold<:MessageGold:755792715257479229> "
            "for this transfer!"
        )

        return

    receiver_account = get_user_account(receiver)

    sender_account["balance"] -= amount
    receiver_account["balance"] += int(
        amount - TRANSFER_TAX_RATE * amount
    )

    store_user_account(sender_account)
    store_user_account(receiver_account)

    await ctx.send(
        f"Transfer successful! (Tax Rate: {int(TRANSFER_TAX_RATE * 100)}%)"
    )


@bot.command()
async def gamble(ctx, amount):
    if not amount.rstrip("%").isdigit():
        await ctx.send("You can't gamble that!")

        return

    user_account = get_user_account(ctx.author)

    balance = user_account["balance"]

    if "%" in amount:
        if not 0 < float(amount.rstrip("%")) <= 100:
            await ctx.send("You can't gamble that!")

            return

        amount = int(float(amount.rstrip("%")) * balance / 100)
    else:
        amount = int(amount)

    if balance < amount:
        await ctx.send(
            "You do not have enough Gold<:MessageGold:755792715257479229> "
            "to gamble that much! "
        )

        return

    outcome = random.randint(0, 1)

    if outcome == 0:
        user_account["balance"] += amount

        store_user_account(user_account)

        await ctx.send("Yay! You doubled your gamble amount!")
    else:
        user_account["balance"] -= amount

        store_user_account(user_account)

        await ctx.send("HAHA YOU LOST!!! YOU IDIOT!")


@bot.command()
@commands.cooldown(1, 5, commands.BucketType.user)
async def bet(ctx, link, amount, time, predicted_ups):
    user = ctx.author

    if not amount.rstrip("%").isdigit() or not predicted_ups.isdigit():
        await ctx.send("You can't bet that!")

        return

    user_account = get_user_account(user)

    if "%" in amount:
        if not 0 < float(amount.rstrip("%")) <= 100:
            await ctx.send("You can't bet that!")

            return

        amount = int(
            float(amount.rstrip("%")) * user_account["balance"] / 100
        )
    else:
        amount = int(amount)

    predicted_ups = int(predicted_ups)
    initial_post = reddit_client.submission(url=link)

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

    if user_account["balance"] < amount:
        await ctx.send("You do not have enough chips to bet this much!")

        return

    if user_account["active_bets"] >= 3:
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
        f"This post has {initial_ups} upvotes right now! You bet {amount} "
        f"Gold<:MessageGold:755792715257479229> on it reaching "
        f"{predicted_ups} upvotes in {time}!"
    )

    user_account["active_bets"] += 1
    user_account["balance"] -= amount

    store_user_account(user_account)

    # waits until the chosen time runs out, then calculates the accuracy
    try:
        await asyncio.sleep(time_in_seconds)
    except Exception as error:
        await ctx.send(error)

    final_post = reddit_client.submission(url=link)
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

    # multiplier formula
    multiplier = (375 / 338) * (accuracy - 0.4) ** 3 * time_in_seconds ** \
                 (2 / 7) * math.log(predicted_ups_difference, 15)

    winnings = int(amount * multiplier)
    true_winnings = winnings - amount

    user_account = get_user_account(user)

    user_account["balance"] += winnings
    user_account["active_bets"] -= 1
    user_account["mean_accuracy"] = calculate_mean_accuracy(
        user_account["mean_accuracy"],
        user_account["total_bets"],
        accuracy
    )
    user_account["total_bets"] += 1

    store_user_account(user_account)

    if true_winnings > 0:
        await ctx.send(
            f"Hello {user.mention}! It's {time} later, and the post has "
            f"{final_ups} upvotes right now! You were {accuracy_in_pct}% "
            f"accurate and won {true_winnings} "
            f"Gold<:MessageGold:755792715257479229>!"
        )
    elif true_winnings == 0:
        await ctx.send(
            f"Hello {user.mention}! It's {time} later, and the post has "
            f"{final_ups} upvotes right now! You were {accuracy_in_pct}% "
            f"accurate but won nothing."
        )
    else:
        await ctx.send(
            f"Hello {user.mention}! It's {time} later, and the post has "
            f"{final_ups} upvotes right now! You were {accuracy_in_pct}% "
            f"accurate and lost {abs(true_winnings)} "
            f"Gold<:MessageGold:755792715257479229>!"
        )


@bot.command()
async def bets(ctx, user_attr=None):
    if not user_attr:
        user = ctx.author
    else:
        user = find_user(ctx, user_attr)
        if not user:
            await ctx.send("This user wasn't found!")

            return

    user_account = get_user_account(user)

    active_bets = user_account["active_bets"]

    await ctx.send(
        f"{'You' if user == ctx.author else f'**{str(user)}**'} currently "
        f"{'have' if user == ctx.author else 'has'} {active_bets} "
        f"{'bets' if active_bets != 1 else 'bet'} running!"
    )


@bot.command(aliases=["statistics"])
async def stats(ctx, user_attr=None):
    if not user_attr:
        user = ctx.author
    else:
        user = find_user(ctx, user_attr)
        if not user:
            await ctx.send("This user wasn't found!")

            return

    user_account = get_user_account(user)

    mean_accuracy = user_account["mean_accuracy"]
    total_bets = user_account["total_bets"]

    embed = discord.Embed(
        title=f"{str(user)}'s Stats",
        color=0x4000ff  # ultramarine
    ).set_thumbnail(
        url="https://imgur.com/UpdCchY.png"
    ).add_field(
        name="Mean accuracy:",
        value=f"{mean_accuracy * 100}%" if mean_accuracy else "NaN",
        inline=False
    ).add_field(
        name="Total bets:",
        value=total_bets,
        inline=False
    )

    await ctx.send(embed=embed)


@bot.command(aliases=["baltop"])
async def balancetop(ctx, size=7):
    guild = ctx.guild

    user_accounts = []

    for member in guild.members:
        user = bot.get_user(member.id)

        if check_user_account(user):
            user_account = get_user_account(user)

            user_accounts.append(user_account)

    # leaderboard is just sorted collection
    collection = {}
    leaderboard = {}

    for user_account in user_accounts:
        balance = user_account["balance"]

        collection[user_account["user_id"]] = balance

    for user_id in sorted(collection, key=collection.get, reverse=True):
        leaderboard[user_id] = collection[user_id]

    embed = discord.Embed(
        title=f"Gold Balance Leaderboard of {str(guild)}",
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

    for user_id in leaderboard:
        user = bot.get_user(user_id)

        embed.add_field(
            name=f"{determine_medal(i)} {str(user)}",
            value=f"{leaderboard[user_id]} "
                  f"Gold<:MessageGold:755792715257479229>",
            inline=False
        )

        if i == size:
            break
        else:
            i += 1

    await ctx.send(embed=embed)


@bot.command(aliases=["acctop"])
async def accuracytop(ctx, size=7):
    guild = ctx.guild

    user_accounts = []

    for member in guild.members:
        user = bot.get_user(member.id)

        if check_user_account(user):
            user_account = get_user_account(user)

            user_accounts.append(user_account)

    # leaderboard is just sorted collection
    collection = {}
    leaderboard = {}

    for user_account in user_accounts:
        mean_accuracy = user_account["mean_accuracy"]

        if mean_accuracy:
            collection[user_account["user_id"]] = mean_accuracy

    for user_id in sorted(collection, key=collection.get, reverse=True):
        leaderboard[user_id] = collection[user_id]

    embed = discord.Embed(
        title=f"Mean Accuracy Leaderboard of {str(guild)}",
        description="*Not on this leaderboard? Go bet on some posts!*",
        color=0x4000ff  # ultramarine

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

    for user_id in leaderboard:
        user = bot.get_user(user_id)

        user_account = get_user_account(user)

        embed.add_field(
            name=f"{determine_medal(i)} {str(user)}",
            value=f"{leaderboard[user_id] * 100}% "
                  f"(Total bets: {user_account['total_bets']})",
            inline=False
        )

        if i == size:
            break
        else:
            i += 1

    await ctx.send(embed=embed)


@bot.command(aliases=["prefix", "prefixes"])
async def prefix_(ctx):
    guild_prefixes = get_guild_prefixes(ctx.guild)

    prefixes = guild_prefixes["prefixes"]

    await ctx.send(
        f"The server {'prefix is' if len(prefixes) == 1 else 'prefixes are'} "
        f"'{', '.join(prefixes)}'!"
    )


@bot.command(aliases=["setprefix", "changeprefixes", "setprefixes"])
@commands.has_permissions(administrator=True)
async def changeprefix(ctx, *, args):
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

    await set_guild_prefixes(ctx.guild, prefixes)

    await ctx.send(
        f"You have changed the server "
        f"{'prefix' if len(prefixes) == 1 else 'prefixes'} to "
        f"'{', '.join(prefixes)}'!"
    )


# error handling for commands
@upvotes.error
async def upvotes_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("You must specify a Reddit post's URL!")


@downvotes.error
async def downvotes_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("You must specify a Reddit post's URL!")


@daily.error
async def daily_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send("You already claimed your daily reward today!")


@repeat.error
async def repeat_error(ctx, error):
    if isinstance(error, commands.CommandError):
        await ctx.send("You must specify what to repeat!")


@balancetop.error
async def balancetop_error(ctx, error):
    if isinstance(error, commands.CommandError):
        await ctx.send("That's not a valid argument!")


@bet.error
async def bet_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(
            f"You must specify arguments! Use: "
            f"*{bot.command_prefix(bot, ctx.message)[0]}bet "
            "[Reddit post link] [bet amount] [time (in s/m/h)] [predicted "
            "upvotes on that post after that time]* to bet."
        )
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send("You have to wait a few seconds between bets!")


@gibcash.error
async def gibcash_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send("You have to wait a few seconds!")


@changeprefix.error
async def changeprefix_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("You must specify a prefix!")
