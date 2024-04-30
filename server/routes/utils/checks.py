import typing
import re


async def validate_pipe_info(js: dict) -> typing.Optional[str]:
  """
  Validate the pipe information provided by a request.
  Return an error message if any.
  """


  if not (description := js.get("description")):
    return "Missing description"

  if len(description) > 500:
    return "Description is too long (max 500 characters)"

  # is valid webhook url?
  # https://discord.com/api/webhooks/<channel>/<secret>

  if not (webhook_url := js.get("webhook_url")) or not re.match(r"https://discord.com/api/webhooks/\d+/\w+", webhook_url):
    return "Invalid Discord Webhook URL"

  return None
