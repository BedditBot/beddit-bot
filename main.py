# Note: If you host the bot on Heroku (https://heroku.com/), you
# need to assign the constants to a Config Vars.

import setup
import events
import commands
from signal import signal, SIGTERM

from config import bot, D_TOKEN
from custom import terminate

signal(SIGTERM, terminate)

bot.run(D_TOKEN)
