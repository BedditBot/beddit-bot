# Note: If you host the bot on Heroku (https://heroku.com/), you
# need to assign the constants to a Config Vars.

import setup
import events
import commands
from signal import signal, SIGTERM
from sys import exit as sys_exit

from config import bot, D_TOKEN
from custom import disconnect_database


async def terminate(_, __):
    print("Terminating...")

    await bot.logout()

    await disconnect_database()

    sys_exit()


signal(SIGTERM, terminate)

bot.run(D_TOKEN)
