import json


# bank format: {
#   "[user_id]": {
#       "balance": [number of bedcoins],
#       "active_bets": [number of active bets]
#   },
#   ...
# }


async def get_bank_data():
    with open("bank.json", "r") as file:
        bank_data = json.load(file)

    return bank_data


# opens an account if the user does not have one already
async def open_account(user):
    bank_data = await get_bank_data()

    if str(user.id) in bank_data:
        return

    bank_data[str(user.id)] = {
        "balance": 100,
        "active_bets": 0
    }

    with open("bank.json", "w") as file:
        json.dump(bank_data, file)
