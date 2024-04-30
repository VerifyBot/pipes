import requests
from discord_webhook import DiscordWebhook

# webhook = DiscordWebhook(url="https://discord.com/api/webhooks/1234544601571000472/N_uZiHgNmE6oI2AuLvp9SSyZzFaI1FgI9kytJTBs0A8WuieKZg9twQkP-LQ3VALIPKj2")
#
with open('abcds.txt', 'rb') as f:
  buff = f.read()

# requests.post(
#   "https://discord.com/api/webhooks/1234544601571000472/N_uZiHgNmE6oI2AuLvp9SSyZzFaI1FgI9kytJTBs0A8WuieKZg9twQkP-LQ3VALIPKj2",
#   files={
#     'file': ('content.txt', buff)
#   }
# )

import asyncio
import aiohttp

async def main():
  form_data = aiohttp.FormData(quote_fields=False)
  form_data.add_field(name='files[0]', value=buff, filename='content.txt', content_type='application/octet-stream')

  async with aiohttp.ClientSession() as session:
    async with session.post(
        'https://discord.com/api/webhooks/1234544601571000472/N_uZiHgNmE6oI2AuLvp9SSyZzFaI1FgI9kytJTBs0A8WuieKZg9twQkP-LQ3VALIPKj2',
        data=form_data,
    ) as resp:

      print(await resp.text())

# response = webhook.execute()

if __name__ == '__main__':
  loop = asyncio.get_event_loop()
  loop.run_until_complete(main())
