"""
Main cogs. Put commands in here that are essential to the functionality of the bot.
"""

import discord, utils

from discord.ext import commands
from defs import db_conn, db_cursor, TIER_NAME_TO_TIER_RANK
from embeds import send_data

class MainCommands(commands.Cog):
    def __init__(self, _bot: discord.Bot):
        self.bot = _bot

    async def cog_command_error(self, ctx: discord.ApplicationContext, error: commands.CommandError):
        await utils.handle_error(ctx=ctx, error=error)

    @commands.slash_command(guild_ids=[1177151218049618031])
    @commands.is_owner()
    async def reload_cogs(self, ctx: discord.ApplicationContext, sync: bool):
        self.bot.reload_extension("commands.main_cogs")
        self.bot.reload_extension("commands.misc_cogs")
        if sync:
            await self.bot.sync_commands()

        await ctx.respond("Reloaded cogs")

    @commands.slash_command(description="Sets a channel where all tracks will appear.")
    @discord.guild_only()
    @discord.commands.option("channel", discord.TextChannel, description="Text channel that the globals will be sent to")
    @commands.check(utils.permissions_check)
    async def set_tracker(self, ctx: discord.ApplicationContext, channel: discord.TextChannel):
        db_cursor.execute(
            """
            INSERT INTO ChannelsPerGuild (guild_id, tracker_channel_id)
            VALUES (?, ?)
            ON CONFLICT(guild_id)
                DO UPDATE SET tracker_channel_id = excluded.tracker_channel_id
            """,
            (ctx.guild_id, channel.id,)
        )
        db_conn.commit()
        await ctx.respond(content=f"Tracker set to {channel.mention}.")

    @commands.slash_command(description="Set a channel where globals will appear.")
    @discord.guild_only()
    @discord.commands.option("channel", discord.TextChannel, description="Text channel that the globals will be sent to")
    @commands.check(utils.permissions_check)
    async def set_global_channel(self, ctx: discord.ApplicationContext, channel: discord.TextChannel):
        tracker_channel_id: list | int = db_cursor.execute(
            "SELECT tracker_channel_id FROM ChannelsPerGuild WHERE guild_id = ?", (ctx.guild_id,)).fetchone()
        if tracker_channel_id is not None and len(tracker_channel_id) != 0:
            tracker_channel_id = tracker_channel_id[0]
            if channel.id == tracker_channel_id:
                return await ctx.respond(content="You cannot set the global channel to same channel as the tracker channel.")

        if tracker_channel_id is None:
            return await ctx.respond(content="Set a tracker channel first.")
        else:
            db_cursor.execute(
                """
                UPDATE ChannelsPerGuild
                SET global_channel_id = ?
                WHERE guild_id = ?
                """,
                (channel.id, ctx.guild_id,)
            )
            db_conn.commit()
        await ctx.respond(content=f"Set global channel set to {channel.mention}.")

    @commands.slash_command(description="Remove the current global channel, if one exists.")
    @discord.guild_only()
    @commands.check(utils.permissions_check)
    async def remove_global_channel(self, ctx: discord.ApplicationContext):
        db_cursor.execute("DELETE FROM ChannelsPerGuild WHERE guild_id = ?", (ctx.guild.id,))
        db_conn.commit()

        await ctx.respond(content=f"Removed global channel.")

    @commands.slash_command(description="Get pinged when the inputted username gets a track.")
    @discord.guild_only()
    @discord.commands.option("username", str, description="Roblox username")
    @discord.commands.option("globals_only", bool, description="Ping for globals only", required=False, default=False)
    async def set_user_ping(self, ctx: discord.ApplicationContext, username: str, globals_only: bool = False):
        # TODO: stax; figure out a better way to do this
        db_cursor.execute(
            """
            INSERT INTO PingsPerUsername (guild_id, username, user_id, globals_only)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(guild_id, username, user_id)
                DO UPDATE SET 
                username = excluded.username,
                globals_only = excluded.globals_only
            """,
            (ctx.guild_id, username, ctx.author.id, globals_only)
        )
        db_conn.commit()
        await ctx.respond(content=f"You will now be pinged by tracks with the user \"{username}\".")

    @commands.slash_command(description="Remove all usernames to be pinged by that were set with set_user_ping.")
    @discord.guild_only()
    async def remove_user_ping(self, ctx: discord.ApplicationContext):
        db_cursor.execute("DELETE FROM PingsPerUsername where user_id = ? AND guild_id = ?",
                          (ctx.author.id, ctx.guild_id,))
        db_conn.commit()
        await ctx.respond(content=f"Removed set pings in this server.")

    @commands.slash_command(description="Track an ore globally under a username. Only usable by whitelisted users.")
    @discord.commands.option("ore_name", str, description="The ore's name", autocomplete=utils.ore_name_autocomplete)
    @discord.commands.option("base_rarity", int, description="The rarity of the ore. Make sure to use variant rarity if it is a variant")
    @discord.commands.option("blocks_mined", int, description="The blocks mined")
    @discord.commands.option("username", str, description="The Roblox username of the person")
    @discord.commands.option("tier", str, description="The tier of the ore", choices=list(TIER_NAME_TO_TIER_RANK.keys()))
    @discord.commands.option("ore_type", str, description="The variant of the ore", choices=["NORMAL", "IONIZED", "SPECTRAL"])
    @discord.commands.option("world", str, description="The world that the ore was found in")
    @discord.commands.option("loadout", str, description="The loadout the person was using")
    @discord.commands.option("event", str, description="The active event during the ore find")
    @discord.commands.option("cave_type", str, description="The cave type that the ore was found in (Not required for cave exclusive ores)", autocomplete=utils.cave_type_autocomplete, required=False, default=None)
    @commands.check(utils.whitelist_check)
    async def manual_track(
        self, ctx: discord.ApplicationContext,
        ore_name: str,
        base_rarity: int,
        blocks_mined: int,
        username: str,
        tier: str,
        ore_type: str,
        world: str,
        loadout: str,
        event: str,
        cave_type: str = None
    ):
        await send_data(ore_name=ore_name, ore_rarity=base_rarity, cave_type=cave_type, ore_tier=tier,
                        ore_type=ore_type, event=event, world=world, username=username, loadout=loadout,
                        blocks_mined=blocks_mined, manual_tracked=True)
        await ctx.respond(content="Sent")

    @commands.slash_command(description="Set a message that will be sent with global tracks.")
    @discord.guild_only()
    @discord.commands.option("message", str, description="The message that will be sent when a global is found. To input roles, use <@&role_id>")
    @commands.check(utils.permissions_check)
    async def set_global_message(self, ctx: discord.ApplicationContext, message: str):
        db_cursor.execute(
            """
            INSERT INTO GlobalMessagePerGuild (guild_id, message)
            VALUES (?, ?)
            ON CONFLICT(guild_id)
                DO UPDATE SET message = excluded.message
            """,
            (ctx.guild_id, message,)
        )
        db_conn.commit()

        await ctx.respond(content=f"Set global message to `{message}`.")

    @commands.slash_command()
    @discord.guild_only()
    @commands.check(utils.permissions_check)
    async def remove_global_message(self, ctx: discord.ApplicationContext):
        db_cursor.execute("DELETE FROM GlobalMessagePerGuild WHERE guild_id = ?", (ctx.guild.id,))
        db_conn.commit()

        await ctx.respond(content=f"Removed global message.")

    @commands.slash_command(description="Add usernames to the list of usernames to be tracked.")
    @discord.guild_only()
    @discord.commands.option("usernames", str, description="A list of usernames to add to the tracker. Separate usernames by a comma")
    @commands.check(utils.permissions_check)
    async def add_to_tracker(self, ctx: discord.ApplicationContext, usernames: str):
        db_cursor.execute(
            """
            SELECT *
            FROM PlayersPerGuild
            WHERE guild_id = ?
            """,
            (ctx.guild_id,),
        )

        selection = db_cursor.fetchall()
        existing_pairs: list[str] = [[x[0], x[1]] for x in selection]

        # allow multiple usernames to be added at once
        to_be_added: list[str] = [u.strip() for u in usernames.split(",")]

        added_users: list[str] = []
        existing_users: list[str] = []
        for name in to_be_added:
            if 3 <= len(name) <= 50:
                if name not in ("@everyone", "@here"):
                    if [ctx.guild_id, name] not in existing_pairs:
                        db_cursor.execute(
                            """
                            INSERT INTO PlayersPerGuild (guild_id, username)
                            VALUES (?, ?)
                            """,
                            (ctx.guild_id, name),
                        )
                        added_users.append(name)
                    else:
                        existing_users.append(name)

        db_conn.commit()

        message: str = ""
        if added_users:
            message += f"Successfully added: {', '.join(f'`{u}`' for u in added_users)}"
        if existing_users:
            if added_users:
                message += f"\nSkipped adding existing users: {', '.join(f'`{u}`' for u in existing_users)}"
            else:
                message += f"Skipped adding existing users: {', '.join(f'`{u}`' for u in existing_users)}"
        if len(message) == 0:
            message = "No users added."

        await ctx.respond(content=message)

    @commands.slash_command(description="Remove usernames from the list of usernames to be tracked.")
    @discord.guild_only()
    @discord.commands.option("usernames", str, description="A list of usernames to remove from the tracker. Separate usernames by a comma")
    @commands.check(utils.permissions_check)
    async def remove_from_tracker(self, ctx: discord.ApplicationContext, usernames: str):
        # allow multiple usernames to be added at once
        to_be_removed: list[str] = [u.strip() for u in usernames.split(",")]

        removed_users: list[str] = []
        for name in to_be_removed:
            if 3 <= len(name) <= 50:
                db_cursor.execute(
                    """
                    DELETE
                    FROM PlayersPerGuild
                    WHERE guild_id = ?
                      AND LOWER(username) = LOWER(?)
                    """,
                    (ctx.guild_id, name),
                )
                removed_users.append(name)

        db_conn.commit()

        await ctx.respond(content=f"Removed users {', '.join(f'`{u}`' for u in removed_users)}")


def setup(_bot: discord.Bot) -> None:
    """
    Expose these commands to the extension system.
    """
    _bot.add_cog(MainCommands(_bot))
