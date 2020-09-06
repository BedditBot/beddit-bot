import json


async def open_account(user):
    bank_data = await get_bank_data()

    if str(user.id) in bank_data:
        return

    bank_data[str(user.id)] = {}
    bank_data[str(user.id)]["wallet"] = 100
    bank_data[str(user.id)]["bets"] = 0

    with open("bank.json", "w") as file:
        json.dump(bank_data, file)


async def get_bank_data():
    with open("bank.json", "r") as file:
        bank_data = json.load(file)

    return bank_data
