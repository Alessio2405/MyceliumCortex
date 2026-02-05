import httpx
import logging
from typing import Optional

logger = logging.getLogger("myceliumcortex.integrations")


class TelegramIntegration:
    def __init__(self, bot_token: str):
        self.bot_token = bot_token
        self.base = f"https://api.telegram.org/bot{self.bot_token}"

    async def send_message(self, chat_id: str, text: str, parse_mode: Optional[str] = "HTML"):
        url = f"{self.base}/sendMessage"
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, json={"chat_id": chat_id, "text": text, "parse_mode": parse_mode})
            if resp.status_code != 200:
                logger.warning("Telegram send_message failed: %s", resp.text)
            return resp.json()


class WhatsAppIntegration:
    def __init__(self, account_sid: str, auth_token: str, phone_number: str):
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.phone_number = phone_number
        self.base = f"https://api.twilio.com/2010-04-01/Accounts/{self.account_sid}"

    async def send_message(self, to_number: str, text: str):
        url = f"{self.base}/Messages.json"
        async with httpx.AsyncClient(auth=(self.account_sid, self.auth_token)) as client:
            payload = {"From": self.phone_number, "To": to_number, "Body": text}
            resp = await client.post(url, data=payload)
            if resp.status_code not in (200, 201):
                logger.warning("WhatsApp (Twilio) send_message failed: %s", resp.text)
            return resp.json()
