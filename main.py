# Note: If you host the bot on Heroku (https://heroku.com/), you
# need to assign the constants to a Config Vars.

import setup
import events
import commands


def run_bot():
    from config import bot, D_TOKEN

    def modify_allowed_mentions():
        import discord

        nonlocal bot

        bot.allowed_mentions = discord.AllowedMentions(
            everyone=False,
            users=True,
            roles=False
        )

    modify_allowed_mentions()

    bot.run(D_TOKEN)


run_bot()
