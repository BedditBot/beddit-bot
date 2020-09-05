#--------------------#
# IMPORTS
#--------------------#
import discord
import asyncio
import praw
from discord.ext import commands
import sys
import time
import math
import json
import os
import random
#--------------------#
# BOOTUP SHIT
#--------------------#
reddit = praw.Reddit(client_id = 'CLIENT ID',
                     client_secret = 'CLIENT SECRET',
                     username='USERNAME',
                     password='PASSWORD',
                     user_agent='USER AGENT')
os.chdir("PATH HERE")
bot = commands.Bot(command_prefix='&')
bad_chars = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z','A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
#--------------------#
# BOT EVENTS
#--------------------#
@bot.event
async def on_ready():
    print('HELLO I HAVE INTERNET I AM {0.user}'.format(bot))

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.startswith('Ping?'):
        latency = round(bot.latency, 3) * 1000  # in ms to 3 d.p.
        await message.channel.send(f"Pong! ({latency}ms)")

    await bot.process_commands(message)
#--------------------#
# BOT COMMANDS
#--------------------#

@bot.command()
async def upvotes(ctx, arg):
    link1 = reddit.submission(url=arg) 
    await ctx.send(f"This post has {link1.ups} upvotes!")

@bot.command()
async def downvotes(ctx, arg):
    link1 = reddit.submission(url=arg) 
    ratio = link1.upvote_ratio
    ups = round((ratio*link1.score)/(2*ratio - 1)) if ratio != 0.5 else round(link1.score/2)
    downs = ups - link1.score
    await ctx.send(f"This post has {downs} downvotes!")

@bot.command()
async def repeat(ctx, *, arg):
    repeat = arg
    if '@everyone' in repeat: 
        await ctx.send("Haha fuck you with your everyone ping nonsense!")
    elif '@here' in repeat: 
        await ctx.send("There's nobody here I guess...")    
    elif 'discord.gg' in repeat:
        await ctx.send("Trying to advertise another server, huh?")
    elif '@' in repeat:
        await ctx.send("No pinging!")
    else:
        await ctx.send(arg)

@bot.command()
async def upstime(ctx, arg, arg2):
    link2 = reddit.submission(url=arg)
    var1 = link2.ups
    await ctx.send(f"This post has {link2.ups} upvotes right now!")
    sleeptime = int(arg2)
    await asyncio.sleep(sleeptime)
    link2 = reddit.submission(url=arg)
    var2 = link2.ups
    var3 = var2 - var1
    await ctx.send(f"It's {arg2} seconds later, and it has {link2.ups} upvotes right now! The difference is {var3} upvotes!")   

@bot.command()
async def bet(ctx, arg, arg2, arg3, arg4):
    link = reddit.submission(url=arg)
    await open_account(ctx.author)
    user = ctx.author
    users = await get_bank_data()
    betamount = arg2
    time = arg3
    time2 = arg3
    prediction = arg4 
    prediction2 = arg4
    firstupvote = link.ups
    prediction = int(prediction)
    betnegativecheck = int(betamount)
    predictioncheck = int(prediction)
#hotfixes for everything people can fuck up
    if firstupvote > prediction:
        await ctx.send("Your prediction can't be lower than the current amount of upvotes!")    
        return
    if betnegativecheck < 0:
        await ctx.send("You can't bet negative numbers!")
        return
    if predictioncheck < 0:
        await ctx.send("You can't bet on negative upvotes!")
        return   
    if users[str(user.id)]["wallet"] < betnegativecheck:
        await ctx.send("You do not have enough chips to bet this much!!")
        return
    if users[str(user.id)]["bets"] >= 3:
        await ctx.send("You already have 3 bets running!")
        return      
    if arg == None or arg2 == None or arg3 == None or arg4 == None:
        await ctx.send("You did not fill in all the arguments!")
        return
    if '@' in arg2:
        await ctx.send("You can't ping people in your arguments!")
    if '@' in arg3:
        await ctx.send("You can't ping people in your arguments!")
    if '@' in arg4:
        await ctx.send("You can't ping people in your arguments!")
    users[str(user.id)]["bets"] += 1
    with open("runningbets.json","w") as f:
        json.dump(users,f)

#Getting time indicator, then removing it and turning time to seconds
    if 's' in time:
        for i in bad_chars: 
            time = time.replace(i, '')
        time2 = int(time)
        timeinseconds = time2
        if time == None:
            await ctx.send("You did not properly specify time!")

    elif 'm' in time:
        for i in bad_chars:
            time = time.replace(i, '')
        time2 = int(time)
        timeinseconds = time2 * 60
        if time == None:
            await ctx.send("You did not properly specify time!")

    elif 'h' in time:
        for i in bad_chars: 
            time = time.replace(i, '') 
        time2 = int(time)
        timeinseconds = time2 * 60 * 60
        if time == None:
            await ctx.send("You did not properly specify time!")

    elif '@' in time:
        await ctx.send("You can't ping people in your arguments!")
        return        
    else:
        await ctx.send("You can't use words as arguments!")
        return
#Sending initial message with specifics
    await ctx.send(f"This post has {link.ups} upvotes right now! You bet {betamount} on it reaching {prediction} in {arg3}!")
#removing bet money from bank account
    users[str(user.id)]["wallet"] -= betnegativecheck
    with open("mainbank.json","w") as f:
        json.dump(users,f)
    balstart = users[str(user.id)]["wallet"]

#Calculatng the prediction multiplier based on how many upvotes were bet on
    if prediction > firstupvote:
        prediction2 = prediction - firstupvote
    if 0 < prediction2 < 500:
        predicmulti = -1
    elif 500 < prediction2 < 1000:
        predicmulti = -0.5
    elif 1000 < prediction2 < 2500:
        predicmulti = 0
    elif 2500 < prediction2 < 5000:
        predicmulti = 0.5
    elif 5000 < prediction2 < 10000:
        predicmulti = 1
    elif 10000 < prediction2 < 20000:
        predicmulti = 1.5
    elif 20000 < prediction2 < 30000:
        predicmulti = 2
    elif 30000 < prediction2 < 40000:
        predicmulti = 2.5
    elif 40000 < prediction2 < 50000:
        predicmulti = 3
    elif 50000 < prediction2 < 60000:
        predicmulti = 3.5
    elif 60000 < prediction2 < 70000:
        predicmulti = 4
    elif 70000 < prediction2 < 80000:
        predicmulti = 5
    elif 80000 < prediction2 < 90000:
        predicmulti = 6
    elif prediction2 > 90000:
        predicmulti = 7.5
    else:
        await ctx.send("Something went wrong! Error: PredicMulti!")


#Calculating the time multiplier based on how long the bet takes
    if 0 < timeinseconds < 61:
        timemulti = -10
    elif 60 < timeinseconds < 301:
        timemulti = -4
    elif 300 < timeinseconds < 3601:
        timemulti = -2
    elif 3600 < timeinseconds < 7201:
        timemulti = 0
    elif 7200 < timeinseconds < 10801:
        timemulti = 0.5
    elif 10800 < timeinseconds < 14401:
        timemulti = 1
    elif 14400 < timeinseconds < 18001:
        timemulti = 1.5
    elif 18000 < timeinseconds < 21601:
        timemulti = 2.3
    elif 21600 < timeinseconds < 25201:
        timemulti = 3.8
    elif 25200 < timeinseconds < 28801:
        timemulti = 4.5
    elif 28800 < timeinseconds < 32401:
        timemulti = 6
    elif 32400 < timeinseconds < 36001:
        timemulti = 7.5
    elif timeinseconds > 36000:
        timemulti = 10
    else:
        await ctx.send(f"Something went wrong... Error: {timeinseconds}")
#Bot sleeping untill the specific time runs out, then calculating the accuracy
    await asyncio.sleep(timeinseconds)
    link2 = reddit.submission(url=arg)
    secondupvote = link2.ups
    if secondupvote > prediction:
        accuracy = prediction / secondupvote * 100
    elif secondupvote < prediction:
        accuracy = secondupvote / prediction * 100
    else:
        accuracy = 100

#Determining the accuracy multiplier based on how precicise the prediction was
    if accuracy < 0:
        accumulti = -2
        await ctx.send("Hmmmm strange times")      
    elif 0 < accuracy < 10:
        accumulti = -2
    elif 10 < accuracy < 20:
        accumulti = -1.5
    elif 20 < accuracy < 30:
        accumulti = -1
    elif 30 < accuracy < 40:
        accumulti = -0.5    
    elif 40 < accuracy < 50:
        accumulti = -0.3
    elif 50 < accuracy < 60:
        accumulti = 0
    elif 60 < accuracy < 70:
        accumulti = 0.5
    elif 70 < accuracy < 80:
        accumulti = 1.5
    elif 80 < accuracy < 90:
        accumulti = 3
    elif 90 < accuracy < 95:
        accumulti = 4.5
    elif 95 < accuracy < 100:
        accumulti = 6.5
    elif accuracy == 100:
        accumulti = 10    
    elif accuracy > 100:
        accumulti = 10
        await ctx.send("Hmmmm strange times 2: electric boogaloo")    
    else:
        await ctx.send("Beep boop accuracy shit is messed up")    
#Final calculations to determine payout
    difference = secondupvote - firstupvote
    multi = predicmulti + timemulti + accumulti
    betamount = int(betamount)
    winnings = betamount * multi
    accuracypost = int(accuracy)
    finalbalance = balstart + winnings
    if winnings > 0:
        await ctx.send(f"It's {arg3} later, and it has {link2.ups} upvotes right now! The difference is {difference} upvotes! You were {accuracypost}% accurate and earned ${winnings}!") 
    else:
        await ctx.send(f"It's {arg3} later, and it has {link2.ups} upvotes right now! The difference is {difference} upvotes! You were {accuracypost}% accurate and unfortunately lost ${winnings}!")
    users[str(user.id)]["bets"] -= 1
    with open("runningbets.json","w") as f:
        json.dump(users,f)     
#Making sure user balance doesn't go negative   
    if finalbalance < 0:
        users[str(user.id)]["wallet"] = 0
        with open("mainbank.json","w") as f:
            json.dump(users,f)              
    else:
        users[str(user.id)]["wallet"] += winnings
        with open("mainbank.json","w") as f:
            json.dump(users,f)    

@bot.command()
async def balance(ctx):
    await open_account(ctx.author)

    user = ctx.author

    users = await get_bank_data()

    wallet_amt = users[str(user.id)]["wallet"]

    em = discord.Embed(title = f"{ctx.author.name}'s Beddit balance", color=0x96d35f)
    em.add_field(name = "Your chips:",value = wallet_amt)
    em.set_thumbnail(url="https://i.imgur.com/vrtyPEN.png")

    await ctx.send(embed = em)

@bot.command()
async def gamble(ctx, arg):
    await open_account(ctx.author)
    user = ctx.author
    users = await get_bank_data()
    betamount = int(arg)
    bet = random.randint(1,2)
    if users[str(user.id)]["wallet"] < betamount:
        await ctx.send("You do not have enough money to bet that much! YOU POOR FUCK LMAO!!!")
        bet = 0
    if betamount < 0:
        await ctx.send("You can't bet negative numbers!")
        bet = 0
    if bet == 1:
        users[str(user.id)]["wallet"] += betamount
        await ctx.send("Yey! You doubled your bet!")
        with open("mainbank.json","w") as f:
            json.dump(users,f)
    if bet == 2:
        await ctx.send("HAHA YOU LOST YOU DIPSHIT")
        users[str(user.id)]["wallet"] -= betamount
        with open("mainbank.json","w") as f:
            json.dump(users,f)

@bot.command()
@commands.has_permissions(manage_messages=True)
async def role(ctx):
    await ctx.send("You have the correct perms!")

@bot.command()
async def gibcash(ctx):
    await open_account(ctx.author)
    user = ctx.author
    users = await get_bank_data()    
    users[str(user.id)]["wallet"] += 1000
    with open("mainbank.json","w") as f:
        json.dump(users,f)
    await ctx.send("I deposited 1000 points to your bank account!")

async def open_account(user):

    users = await get_bank_data()

    if str(user.id) in users:
        return False
    else:
        users[str(user.id)] = {}
        users[str(user.id)]["wallet"] = 100
        users[str(user.id)]["bets"] = 0

    with open("mainbank.json","w") as f:
        json.dump(users,f)
    return True

async def get_bank_data():
    with open("mainbank.json","r") as f:
        users = json.load(f)
    return users

#--------------------#
# ERROR HANDLING
#--------------------#

@upvotes.error
async def upvotes_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('You must specify a Reddit URL!')    

@downvotes.error
async def downvotes_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('You must specify a Reddit URL!')    

@bet.error
async def bet_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("You must specify arguments! Use: *'bet [reddit link] [bet amount] [time (s/m/h)] [upvotes on that post at that time]'*")  

@repeat.error
async def repeat_error(ctx, error):
    if isinstance(error, commands.CommandError):
        await ctx.send('You must specify what to repeat!')      

#--------------------#
# BOT TOKEN GOES HERE
#--------------------#

bot.run('TOKEN HERE')