import aiohttp


class OAuthError(Exception):
  pass


API_ENDPOINT = "https://discord.com/api/v10"


async def get_access_token_from_code(code: str, client_id: str, client_secret: str, server_url: str):
  """
  Get the access token & refresh token from Discord using the code
  """

  data = dict(
    grant_type='authorization_code',
    code=code,
    redirect_uri=server_url + '/oauth2/callback',
  )

  auth = aiohttp.BasicAuth(client_id, client_secret)
  async with aiohttp.ClientSession() as cs:
    async with cs.post(API_ENDPOINT + "/oauth2/token", data=data, auth=auth) as resp:
      js = await resp.json()

      if resp.status != 200:
        raise OAuthError(js)

      return js


async def fetch_user_info(access_token: str):
  """
  Get the user's info from Discord
  """

  async with aiohttp.ClientSession() as session:
    async with session.get(API_ENDPOINT + "/users/@me", headers={"Authorization": "Bearer " + access_token}) as resp:
      js = await resp.json()

      if resp.status != 200:
        raise Exception(js)

      return js
