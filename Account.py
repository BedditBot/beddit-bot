import discord

import config

connection = config.connection


class Account:
    def __init__(
            self,
            user_id,
            gold,
            active_bets,
            total_bets,
            mean_accuracy,
            platinum
    ):
        self.user_id = user_id
        self.gold = gold
        self.active_bets = active_bets
        self.total_bets = total_bets
        self.mean_accuracy = mean_accuracy
        self.platinum = platinum

    @staticmethod
    async def open(user):
        await user.send(
            embed=discord.Embed(
                title="Warning",
                colour=0xffffff,
                description="Gambling addiction can develop from gambling fake"
                            " virtual currency, like in Beddit, and negatively"
                            " affects self-esteem, relationships, "
                            "physical/mental health, school/work performance "
                            "and social life.\nBeddit **does not encourage or "
                            "promote** any kind of **gambling** with real "
                            "currency, **we discourage it**.\nIn case you "
                            "think you may have developed gambling addiction, "
                            "please seek help from [professionals]"
                            "(https://www.ncpgambling.org/5475-2/)."
            )
        )

        cursor = connection.cursor()

        cursor.execute(
            "INSERT INTO accounts VALUES (%(user_id)s, %(gold)s, %(platinum)s,"
            " %(active_bets)s, %(total_bets)s, %(mean_accuracy)s);",
            {
                "user_id": user.id,
                "gold": 250,
                "platinum": 0,
                "active_bets": 0,
                "total_bets": 0,
                "mean_accuracy": None
            }
        )

        connection.commit()
        cursor.close()

    @staticmethod
    async def get(user):
        cursor = connection.cursor()

        cursor.execute(
            "SELECT * FROM accounts WHERE user_id=%(user_id)s;",
            {"user_id": user.id}
        )

        values = cursor.fetchone()

        if not values:
            await Account.open(user)

            cursor.execute(
                "SELECT * FROM accounts WHERE user_id=%(user_id)s;",
                {"user_id": user.id}
            )

            values = cursor.fetchone()

        cursor.close()

        account = Account(*values)

        if account.mean_accuracy:
            account.mean_accuracy = float(account.mean_accuracy)

        return account

    async def store(self):
        if self.gold < 0:
            self.gold = 0

        if self.gold > 2147483647:
            self.gold = 2147483647

        cursor = connection.cursor()

        cursor.execute(
            "UPDATE accounts "
            "SET gold = %(gold)s, platinum = %(platinum)s, active_bets = "
            "%(active_bets)s, total_bets = %(total_bets)s, mean_accuracy = "
            "%(mean_accuracy)s WHERE user_id = %(user_id)s;",
            {
                "user_id": self.user_id,
                "gold": self.gold,
                "platinum": self.platinum,
                "active_bets": self.active_bets,
                "total_bets": self.total_bets,
                "mean_accuracy": self.mean_accuracy
            }
        )

        connection.commit()
        cursor.close()

    @staticmethod
    async def check(user):
        cursor = connection.cursor()

        cursor.execute(
            "SELECT * FROM accounts WHERE user_id=%(user_id)s;",
            {"user_id": user.id}
        )

        account_ = cursor.fetchone()

        cursor.close()

        return bool(account_)
