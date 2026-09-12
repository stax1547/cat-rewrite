import re

import dotenv

dotenv_path: str = dotenv.find_dotenv()
if dotenv_path == "":
    raise RuntimeError("Can't find a .env file to load!")

dotenv_values: dict[str, str | None] = dotenv.dotenv_values(dotenv_path=dotenv_path)
if dotenv_values is None:
    raise RuntimeError("Failed to load environment variables, can't continue.")

# If any of these are missing from the file it will fail, which is what we want
DEV_MODE: bool = eval(dotenv_values["DEV_MODE"]) if dotenv_values["DEV_MODE"] is not None else False
BOT_TOKEN: str = dotenv_values["BOT_TOKEN"]

# It's fine if this one is missing
WEBHOOK_LINK: str | None = dotenv_values.get("GLAGGLELAND_WEBHOOK", None)
if WEBHOOK_LINK is not None:
    # Validate the webhook token (taken from discord.Webhook.from_url())
    m: re.Match[str] | None = re.search(r"discord(?:app)?.com/api/webhooks/(?P<id>\d{17,20})/(?P<token>[\w\.\-_]{60,68})", WEBHOOK_LINK)
    if m is None:
        raise ValueError("Invalid webhook URL in .env!")
