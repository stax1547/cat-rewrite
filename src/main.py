import dotenv
import os
import re
import traceback

from commands.cogs import setup_commands
from utils.defs import *
from utils.embeds import send_data


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
            username TEXT NOT NULL,
            PRIMARY KEY(guild_id, username)
        )
        """
    )

    # stax; Holds the global message used to send with trackers in each server.
    db_cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS "GlobalMessagePerGuild"
        (
            guild_id INTEGER PRIMARY KEY,
            message TEXT NOT NULL
        )
        """
    )

    # stax; Holds the channels used to send trackers to in each server.
    db_cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS "ChannelsPerGuild"
        (
            guild_id INTEGER PRIMARY KEY,
            tracker_channel_id INTEGER NOT NULL,
            global_channel_id INTEGER
        )
        """
    )

    # stax; Holds the users to ping when a username is tracked. Server-dependent
    db_cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS "PingsPerUsername"
        (
            guild_id INTEGER NOT NULL,
            username TEXT NOT NULL,
            user_id INTEGER NOT NULL,
            PRIMARY KEY(guild_id, username, user_id)
        )
        """
    )

    db_conn.commit()


def main() -> None:
    """
    Main function. Runs the bot.
    """

    @bot.event
    async def on_connect() -> None:
        print("Ready")  # stax; do not remove this! cybrancee shits itself if you don't print ready

        if bot.auto_sync_commands:
            await bot.sync_commands()

    @bot.event
    async def on_message(message: discord.Message) -> None:
        if message.channel.id in REX_TRACKER_CHANNEL_IDS and message.author.id in REX_WEBHOOK_UIDS and bot.is_ready() == True:
            message_data: discord.Message = await message.channel.fetch_message(
                message.id)  # stax; needed because webhooks dont contain embed data in on_message
            embed_data: discord.Embed = message_data.embeds[0]

            world: str = embed_data.description
            fields = embed_data.fields
            ore_type = TYPE_BY_CHANNEL_IDS.get(message.channel.id, None)

            reg = re.match("\*\*([a-zA-Z0-9_]+)\*\*.*\*\*(.*)\*\*(?:.*\(\*(.* Cave)\*\))?", embed_data.title)
            username: str = reg.group(1)
            ore_name: str = reg.group(2)
            cave_type: str | None = reg.group(3)

            tier: str = TIER_COLOR_TO_TIER_NAME.get(str(embed_data.color), None)
            if tier is None:
                logger.error(f"\nMissing color for tier: {str(embed_data.color)} {type(str(embed_data.color))}")
                logger.debug(f"{embed_data.color.r}, {embed_data.color.g}, {embed_data.color.b}, {embed_data.color}\n")

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
                manual_tracked=False
            )

    try:
        create_database()
        setup_commands(bot)

        dotenv.load_dotenv()
        bot.run(os.getenv("BOT_TOKEN"))
    except:
        trace: str = traceback.format_exc()
        logger.error(msg=trace)
        print("\n\n\nbot failed to start!!!\n\n\n")


if __name__ == "__main__":
    main()
