import asyncio
import re
import traceback
from typing import NoReturn

import config
from commands.cogs import setup_commands
from defs import *
from embeds import send_data


def create_database() -> None:
    """
    Creates the database file and its tables if either do not exist.
    """

    # stax; Holds the usernames tracked in each server.
    db_cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS "PlayersPerGuild"
        (
            guild_id INTEGER NOT NULL,
            username TEXT    NOT NULL,
            PRIMARY KEY (guild_id, username)
        )
        """
    )

    # stax; Holds the global message used to send with trackers in each server.
    db_cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS "GlobalMessagePerGuild"
        (
            guild_id INTEGER PRIMARY KEY,
            message  TEXT NOT NULL
        )
        """
    )

    # stax; Holds the channels used to send trackers to in each server.
    db_cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS "ChannelsPerGuild"
        (
            guild_id           INTEGER PRIMARY KEY,
            tracker_channel_id INTEGER NOT NULL,
            global_channel_id  INTEGER
        )
        """
    )

    # stax; Holds the users to ping when a username is tracked. Server-dependent
    db_cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS "PingsPerUsername"
        (
            guild_id INTEGER NOT NULL,
            username TEXT    NOT NULL,
            user_id  INTEGER NOT NULL,
            globals_only BOOLEAN NOT NULL DEFAULT FALSE,
            PRIMARY KEY (guild_id, username, user_id)
        )
        """
    )

    # stax; Holds the adjusted rarity preferences for guilds
    db_cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS "AdjustedPreferencesPerGuild"
        (
            guild_id   INTEGER PRIMARY KEY,
            preference INTEGER NOT NULL DEFAULT 2
        )
        """
    )

    db_conn.commit()


async def update_presence() -> NoReturn:
    while True:
        logger.info("Updating presence...")

        guild_count: int = db_cursor.execute("SELECT COUNT(*) FROM ChannelsPerGuild", ).fetchone()[0]
        activity: discord.Game = discord.Game(name=f"Tracking in {guild_count} servers!")

        await bot.change_presence(activity=activity)

        await asyncio.sleep(60 * 10)  # Update our presence every 10 minutes.


def fix_up_database() -> None:
    return


def main() -> None:
    """
    Main function. Runs the bot.
    """

    @bot.listen()
    async def on_connect() -> None:
        print("Bot has connected.")
        logger.debug("Bot has connected.")

    @bot.listen()
    async def on_disconnect() -> None:
        print("Bot has disconnected.")
        logger.debug("Bot has disconnected.")

    @bot.listen(once=True)
    async def on_ready() -> None:
        if bot.user is None:
            return

        print(f"Bot has logged in as \"{bot.user.name}\".")
        logger.debug(f"Bot has logged in as \"{bot.user.name}\".")

        asyncio.create_task(update_presence())

        print("Ready")  # stax; do not remove this!

    @bot.listen()
    async def on_message(message: discord.Message) -> None:
        if not bot.is_ready():
            return

        if message.channel.id in REX_TRACKER_CHANNEL_IDS and message.author.id in REX_WEBHOOK_UIDS:
            message_data: discord.Message = await message.channel.fetch_message(
                message.id)  # stax; needed because webhooks dont contain embed data in on_message
            embed_data: discord.Embed = message_data.embeds[0]

            world: str | None = embed_data.description
            fields: list[discord.EmbedField] = embed_data.fields
            ore_type: str = TYPE_BY_CHANNEL_IDS[message.channel.id]

            if embed_data.title is None:
                logger.error("[on_message] Found a valid message but failed to parse the embed title!\nTitle: None")
                return
            
            reg: re.Match | None = re.match(r"\*\*([a-zA-Z0-9_]+)\*\*.*\*\*(.*)\*\*(?:.*\(\*(.* Cave)\*\))?", embed_data.title)
            if reg is None:
                logger.error(f"[on_message] Found a valid message but failed to parse the embed title!\nTitle: {embed_data.title}")
                return

            username: str = reg.group(1)
            ore_name: str = reg.group(2)
            cave_type: str | None = reg.group(3)

            tier: TierNames | None = None
            if embed_data.color is not None:
                tier = TIER_COLOR_TO_TIER_NAME.get(str(embed_data.color), None)
                if tier is None:
                    logger.error(f"[on_message] Missing color for tier: {embed_data.color!s} {type(str(embed_data.color))}")
                    logger.debug(f"[on_message] {embed_data.color.r}, {embed_data.color.g}, {embed_data.color.b}, {embed_data.color}\n")

            base_rarity: int = int(float(fields[0].value.split()[0].replace("1/", "").replace(",", "")))
            blocks_mined: int = int(fields[1].value.replace(",", ""))
            event: str = fields[2].value
            loadout: str = fields[3].value

            await send_data(
                ore_name=ore_name,
                ore_rarity=base_rarity,
                cave_type=cave_type,
                ore_tier=tier,
                ore_type=ore_type,
                event=event,
                world=world,
                username=username,
                loadout=loadout,
                blocks_mined=blocks_mined,
                manual_tracked=False,
            )

    try:
        create_database()
        #fix_up_database()
        setup_commands(bot)

        bot.run(config.BOT_TOKEN)
    except:
        trace: str = traceback.format_exc()
        logger.error(msg=trace)

        separator: str = "-" * 50
        print(f"\n{separator}\nBot failed to start!!!\n{trace}\n{separator}\n")


if __name__ == "__main__":
    main()
