import os

import config

# see line 61
import logging


def logging_setup():
    # Discord
    discord_logger = logging.getLogger("discord")
    discord_logger.setLevel(logging.DEBUG)

    discord_file_handler = logging.FileHandler(
        filename="discord.log",
        encoding="utf-8",
        mode="a"
    )

    discord_console_handler = logging.StreamHandler()
    discord_console_handler.setLevel(logging.WARNING)

    discord_formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(name)s: %(message)s"
    )
    discord_file_handler.setFormatter(discord_formatter)
    discord_console_handler.setFormatter(discord_formatter)

    discord_logger.addHandler(discord_file_handler)
    discord_logger.addHandler(discord_console_handler)

    # Reddit (praw module)
    reddit_file_handler = logging.FileHandler(
        filename="reddit.log",
        encoding="utf-8",
        mode="a"
    )

    reddit_console_handler = logging.StreamHandler()
    reddit_console_handler.setLevel(logging.WARNING)

    praw_logger = logging.getLogger("praw")
    praw_logger.setLevel(logging.DEBUG)

    praw_logger.addHandler(reddit_file_handler)
    praw_logger.addHandler(reddit_console_handler)

    prawcore_logger = logging.getLogger("prawcore")
    prawcore_logger.setLevel(logging.DEBUG)

    prawcore_logger.addHandler(reddit_file_handler)
    prawcore_logger.addHandler(reddit_console_handler)


def check_environment():
    global on_heroku

    if "DYNO" in os.environ:
        on_heroku = True
    else:
        on_heroku = False


def handle_constants():
    if not on_heroku:
        choice = input(
            "Have any constants changed or NOT been set? (y/n) - "
        ).lower().strip(" ")

        if choice in ("y", "yes"):
            token_input = input(
                "Input Discord bot token: "
            ).strip(" ")
            client_id_input = input(
                "Input Reddit client ID: "
            ).strip(" ")
            client_secret_input = input(
                "Input Reddit client secret: "
            ).strip(" ")
            username_input = input(
                "Input Reddit username: "
            ).strip(" ")
            password_input = input(
                "Input Reddit password: "
            ).strip(" ")
            user_agent_input = input(
                "Input Reddit user agent: "
            ).strip(" ")

            # creates a file called ".env" and stores the constants
            with open(".env", "w") as file:
                file.write(
                    f"TOKEN={token_input}\n"
                    f"CLIENT_ID={client_id_input}\n"
                    f"CLIENT_SECRET={client_secret_input}\n"
                    f"USERNAME={username_input}\n"
                    f"PASSWORD={password_input}\n"
                    f"USER_AGENT=\"{user_agent_input}\"\n"
                )

            del token_input
            del client_id_input
            del client_secret_input
            del username_input
            del password_input
            del user_agent_input
        elif choice in ("n", "no"):
            pass
        else:
            print("Invalid input, try again.")
            handle_constants()

        from dotenv import load_dotenv

        load_dotenv()

    config.TOKEN = os.environ["TOKEN"]
    config.CLIENT_ID = os.environ["CLIENT_ID"]
    config.CLIENT_SECRET = os.environ["CLIENT_SECRET"]
    config.USERNAME = os.environ["USERNAME"]
    config.PASSWORD = os.environ["PASSWORD"]
    config.USER_AGENT = os.environ["USER_AGENT"]


def handle_files():
    try:
        with open("bank.json", "r"):
            pass
    except FileNotFoundError:
        with open("bank.json", "w") as file:
            file.write("{\n}")


logging_setup()

on_heroku = None
check_environment()

handle_constants()

handle_files()
