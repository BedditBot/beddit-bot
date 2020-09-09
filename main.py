# Note: If you host the bot on Heroku (https://heroku.com/), you
# need to assign the constants to a Config Vars.

import setup
import events
import commands

from custom import clear_active_bets


def run_bot():
    from config import bot, D_TOKEN

    bot.run(D_TOKEN)


run_bot()

clear_active_bets()
