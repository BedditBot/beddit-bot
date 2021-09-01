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

        async with connection.transaction():
            await connection.execute(
                "INSERT INTO accounts VALUES ($1, $2, $3, $4, $5, $6);",
                user.id,
                250,
                0,
                0,
                None,
                0
            )

    @staticmethod
    async def get(user):
        async with connection.transaction():
            values = tuple(await connection.fetchrow(
                "SELECT * FROM accounts WHERE user_id=$1;",
                user.id
            ).values())

        if not values:
            await Account.open(user)

            async with connection.transaction():
                values = tuple(connection.fetchrow(
                    "SELECT * FROM accounts WHERE user_id=$1;",
                    user.id
                ).values())

        account = Account(*values)

        if account.mean_accuracy:
            account.mean_accuracy = float(account.mean_accuracy)

        return account

    async def store(self):
        if self.gold < 0:
            self.gold = 0

        if self.gold > 2147483647:
            self.gold = 2147483647

        async with connection.transaction():
            await connection.execute(
                "UPDATE accounts SET gold = $2, platinum = $3, "
                "active_bets = $4, total_bets = $5, mean_accuracy = $6 "
                "WHERE user_id = $1;",
                self.user_id,
                self.gold,
                self.platinum,
                self.active_bets,
                self.total_bets,
                self.mean_accuracy
            )

    @staticmethod
    async def check(user):
        async with connection.transaction():
            account_ = tuple(await connection.fetchrow(
                "SELECT * FROM accounts WHERE user_id=$1;",
                user.id
            ).values())

        return bool(account_)
