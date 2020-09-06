import sys
import os

import praw
import asyncio
import discord
import random
from discord.ext import commands
import config
from custom import *

os.chdir(config.filepath)


bot = config.bot

reddit_client = praw.Reddit(client_id=config.CLIENT_ID,
                            client_secret=config.CLIENT_SECRET,
                            username=config.USERNAME,
                            password=config.PASSWORD,
                            user_agent=config.USER_AGENT)


# closes the bot (only bot owners)
@bot.command(hidden=True)
async def cease(ctx):
    if not await bot.is_owner(ctx.author):
        return

    await ctx.send("Farewell...")
    print("Done.")

    await bot.close()
    sys.exit()


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
    if '@everyone' in phrase:
        await ctx.send("Haha fuck you with your everyone ping nonsense!")
    elif '@here' in phrase:
        await ctx.send("There's nobody here I guess...")
    elif 'discord.gg' in phrase:
        await ctx.send("Trying to advertise another server, huh?")
    elif '@' in phrase:
        await ctx.send("No pinging!")
    else:
        await ctx.send(phrase)


@bot.command()
async def upstime(ctx, link, seconds):
    initial_post = reddit_client.submission(url=link)
    initial_ups = initial_post.ups

    sleep_time = int(seconds)

    await ctx.send(f"This post has {initial_ups} upvotes right now!")

    await asyncio.sleep(sleep_time)

    final_post = reddit_client.submission(url=link)
    final_ups = final_post.ups
    ups_difference = final_ups - initial_ups
    await ctx.send(
        f"It's {seconds} seconds later, and it has "
        f"{final_ups} upvotes right now! The difference is "
        f"{ups_difference} upvotes!"
    )


bad_chars = (
    "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m",
    "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"
)


@bot.command()
async def bet(ctx, link, bet_amount, chosen_time, predicted_ups):
    user = ctx.author
    time_for_message = chosen_time

    try:
        bet_amount = int(bet_amount)
        predicted_ups = int(predicted_ups)
    except ValueError:
        await ctx.send("You didn't input the correct data types!")

    initial_post = reddit_client.submission(url=link)
    initial_ups = initial_post.ups

    await open_account(user)
    bank_data = await get_bank_data()

    # hotfixes for everything people can abuse
    if predicted_ups <= initial_ups:
        await ctx.send(
            "Your predicted upvotes can't be lower than or equal to the "
            "current amount of upvotes!"
        )

        return

    if bet_amount < 0:
        await ctx.send("You can't bet negative amounts!")

        return

    if predicted_ups < 0:
        await ctx.send("You can't bet on negative upvotes!")

        return

    if bank_data[str(user.id)]["wallet"] < bet_amount:
        await ctx.send("You do not have enough chips to bet this much!")

        return

    if bank_data[str(user.id)]["bets"] >= 3:
        await ctx.send("You already have 3 bets running!")

        return

    if None in (link, bet_amount, chosen_time, predicted_ups):
        await ctx.send("You did not fill in all the arguments!")

        return

    if "@" in chosen_time:
        await ctx.send("You can't ping people in your arguments!")

        return

    bank_data[str(user.id)]["bets"] += 1

    with open("bank.json", "w") as file:
        json.dump(bank_data, file)

    # gets time unit, then removes it and converts time to seconds

    if "s" in chosen_time:
        for char in bad_chars: 
            chosen_time = chosen_time.replace(char, '')  

        chosen_time_in_seconds = int(chosen_time)
    elif "m" in chosen_time:
        for char in bad_chars: 
            chosen_time = chosen_time.replace(char, '')  

        chosen_time_in_seconds = int(chosen_time) * 60
    elif "h" in chosen_time:
        for char in bad_chars: 
            chosen_time = chosen_time.replace(char, '')  

        chosen_time_in_seconds = int(chosen_time) * 60 * 60
    elif chosen_time.isdigit():
        await ctx.send("Please specify a time unit.")

        return
    else:
        await ctx.send("You can't use words as arguments!")

        return

    if chosen_time_in_seconds < 0:
        await ctx.send("You can't input negative time!")

    # sends initial message with specifics
    await ctx.send(
        f"This post has {initial_ups} upvotes right now! You bet {bet_amount} "
        f"chips on it reaching {predicted_ups} upvotes in {time_for_message}!"
    )

    # removes bet amount from bank account
    bank_data[str(user.id)]["wallet"] -= bet_amount
    with open("bank.json", "w") as file:
        json.dump(bank_data, file)

    initial_balance = bank_data[str(user.id)]["wallet"]

    # calculates the prediction multiplier based on the predicted upvotes
    predicted_ups_increase = predicted_ups - initial_ups

    if predicted_ups_increase < 40000:
        if predicted_ups_increase < 5000:
            if predicted_ups_increase < 1000:
                if predicted_ups_increase < 500:
                    prediction_multiplier = -1
                else:
                    prediction_multiplier = -0.5
            else:
                if predicted_ups_increase < 2500:
                    prediction_multiplier = 0
                else:
                    prediction_multiplier = 0.5
        else:
            if predicted_ups_increase < 20000:
                if predicted_ups_increase < 10000:
                    prediction_multiplier = 1
                else:
                    prediction_multiplier = 1.5
            else:
                if predicted_ups_increase < 30000:
                    prediction_multiplier = 2
                else:
                    prediction_multiplier = 2.5
    else:
        if predicted_ups_increase < 80000:
            if predicted_ups_increase < 60000:
                if predicted_ups_increase < 50000:
                    prediction_multiplier = 3
                else:
                    prediction_multiplier = 3.5
            else:
                if predicted_ups_increase < 70000:
                    prediction_multiplier = 4
                else:
                    prediction_multiplier = 5
        else:
            if predicted_ups_increase < 90000:
                prediction_multiplier = 6
            else:
                prediction_multiplier = 7.5

    # calculates the time multiplier based on the chosen time
    if chosen_time_in_seconds < 21600:
        if chosen_time_in_seconds < 7200:
            if chosen_time_in_seconds < 300:
                if chosen_time_in_seconds < 60:
                    time_multiplier = -10
                else:
                    time_multiplier = -4
            else:
                if chosen_time_in_seconds < 3600:
                    time_multiplier = -2
                else:
                    time_multiplier = 0
        else:
            if chosen_time_in_seconds < 14400:
                if chosen_time_in_seconds < 10800:
                    time_multiplier = 0.5
                else:
                    time_multiplier = 1
            else:
                if chosen_time_in_seconds < 18000:
                    time_multiplier = 1.5
                else:
                    time_multiplier = 2.3
    else:
        if chosen_time_in_seconds < 28800:
            if chosen_time_in_seconds < 25200:
                time_multiplier = 3.8
            else:
                time_multiplier = 4.5
        else:
            if chosen_time_in_seconds < 32400:
                time_multiplier = 6
            elif chosen_time_in_seconds < 36000:
                time_multiplier = 7.5
            else:
                time_multiplier = 10

    # waits until the chosen time runs out, then calculates the accuracy
    await asyncio.sleep(chosen_time_in_seconds)

    final_post = reddit_client.submission(url=link)
    final_ups = final_post.ups

    if final_ups > predicted_ups:
        try:
            accuracy = predicted_ups / final_ups * 100
        except ZeroDivisionError:
            await ctx.send("Oops! Something went wrong.")

            return
    elif final_ups < predicted_ups:
        accuracy = final_ups / predicted_ups * 100
    else:
        accuracy = 100

    # determines the accuracy multiplier based on
    # how accurate the prediction was
    if accuracy < 70:
        if accuracy < 30:
            if accuracy < 10:
                if accuracy <= 0:
                    accuracy_multiplier = -2

                    await ctx.send("Hmm... Strange times.")
                else:
                    accuracy_multiplier = -2
            else:
                if accuracy < 20:
                    accuracy_multiplier = -1.5
                else:
                    accuracy_multiplier = -1
        else:
            if accuracy < 50:
                if accuracy < 40:
                    accuracy_multiplier = -0.5
                else:
                    accuracy_multiplier = -0.3
            else:
                if accuracy < 60:
                    accuracy_multiplier = 0
                else:
                    accuracy_multiplier = 0.5
    else:
        if accuracy < 90:
            if accuracy < 80:
                accuracy_multiplier = 1.5
            else:
                accuracy_multiplier = 3
        else:
            if accuracy < 95:
                accuracy_multiplier = 4.5
            elif accuracy < 100:
                accuracy_multiplier = 6.5
            else:
                accuracy_multiplier = 10

    # final calculations to determine payout
    ups_difference = final_ups - initial_ups

    multiplier = prediction_multiplier + time_multiplier + accuracy_multiplier
    winnings = bet_amount * multiplier
    final_balance = initial_balance + winnings

    accuracy = int(accuracy)

    if winnings > 0:
        await ctx.send(
            f"Hello {user.mention}! It's {time_for_message} later, and it has "
            f"{final_ups} upvotes right now! The difference is "
            f"{ups_difference} upvotes! You were {accuracy}% accurate and "
            f"won ${winnings}!"
        )
    elif winnings == 0:
        await ctx.send(
            f"It's {time_for_message} later, and it has {final_ups} upvotes right "
            f"now! The difference is {ups_difference} upvotes! You were "
            f"{accuracy}% accurate but earned nothing."
        )
    else:
        await ctx.send(
            f"It's {time_for_message} later, and it has {final_ups} upvotes right "
            f"now! The difference is {ups_difference} upvotes! You were "
            f"{accuracy}% accurate and unfortunately lost "
            f"${abs(winnings)}!"
        )

    bank_data[str(user.id)]["bets"] -= 1
    with open("bank.json", "w") as file:
        json.dump(bank_data, file)

    # makes sure user balance doesn't go negative
    if final_balance < 0:
        bank_data[str(user.id)]["wallet"] = 0
        with open("bank.json", "w") as file:
            json.dump(bank_data, file)
    else:
        bank_data[str(user.id)]["wallet"] += winnings
        with open("bank.json", "w") as file:
            json.dump(bank_data, file)


@bot.command()
async def balance(ctx):
    user = ctx.author

    await open_account(user)
    bank_data = await get_bank_data()

    user_balance = bank_data[str(user.id)]["wallet"]

    embed = discord.Embed(
        title=f"{user.name}'s Beddit balance",
        color=0x96d35f
    )
    embed.add_field(name="Your chips:", value=user_balance)
    embed.set_thumbnail(url="https://i.imgur.com/vrtyPEN.png")

    await ctx.send(embed=embed)

@bot.command(pass_context=True)
@commands.cooldown(1, 60*60*24, commands.BucketType.user)
async def daily(ctx):
    user = ctx.author

    await open_account(user)
    bank_data = await get_bank_data()

    bank_data[str(user.id)]["wallet"] += 100
    with open("bank.json", "w") as file:
        json.dump(bank_data, file)    
    await ctx.send("You collected your daily reward of $100!")

@bot.command()
async def gamble(ctx, gamble_amount):
    user = ctx.author

    gamble_amount = int(gamble_amount)

    await open_account(user)
    bank_data = await get_bank_data()

    if bank_data[str(user.id)]["wallet"] < gamble_amount:
        await ctx.send("You do not have enough money to gamble that much! YOU ARE POOR LOL!!!")

        return

    if gamble_amount < 0:
        await ctx.send("You can't gamble negative amounts!")

        return

    outcome = random.randint(0, 1)

    if outcome == 0:
        bank_data[str(user.id)]["wallet"] += gamble_amount

        with open("bank.json", "w") as file:
            json.dump(bank_data, file)

        await ctx.send("Yay! You doubled your gamble amount!")
    else:
        bank_data[str(user.id)]["wallet"] -= gamble_amount

        with open("bank.json", "w") as file:
            json.dump(bank_data, file)

        await ctx.send("HAHA YOU LOST!!! YOU IDIOT!")


@bot.command()
@commands.has_permissions(manage_messages=True)
async def role(ctx):
    await ctx.send("You have the correct permissions!")


@bot.command()
@commands.has_permissions(manage_messages=True)
async def gibcash(ctx):
    user = ctx.author

    await open_account(user)
    bank_data = await get_bank_data()

    bank_data[str(user.id)]["wallet"] += 1000
    with open("bank.json", "w") as file:
        json.dump(bank_data, file)

    await ctx.send("I deposited 1000 chips to your bank account!")


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

@bet.error
async def bet_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(
            f"You must specify arguments! Use: *{bot.command_prefix}bet "
            "[Reddit post link] [bet amount] [time (in s/m/h)] [predicted "
            "upvotes on that post after that time]* to bet."
        )


@repeat.error
async def repeat_error(ctx, error):
    if isinstance(error, commands.CommandError):
        await ctx.send("You must specify what to repeat!")
