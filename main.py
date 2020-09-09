# Note: If you host the bot on Heroku (https://heroku.com/), you
# need to assign the constants to a Config Vars.

import setup
import events
import commands

from custom import clear_active_bets


def set_bot_prefix():
    from config import bot, D_PREFIX

    if not D_PREFIX:
        return

    bot.command_prefix = D_PREFIX


def run_bot():
    from config import bot, D_TOKEN

    bot.run(D_TOKEN)


set_bot_prefix()

run_bot()

clear_active_bets()
