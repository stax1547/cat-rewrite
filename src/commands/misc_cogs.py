"""
Miscellaneous cogs. Put commands in here that are non-essential to the functionality of the bot.
"""

import traceback

from discord.ext import commands

from utils.defs import *
from utils.utils import is_owner


class MiscCommands(commands.Cog):
    def __init__(self, _bot: discord.Bot):
        self.bot = _bot

    async def cog_command_error(self, ctx: discord.ApplicationContext, error: Exception):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.respond(f"This command is on cooldown. Retry in {error.retry_after} seconds")
            return
        elif isinstance(error, commands.NotOwner):
            await ctx.respond(f"You are not the owner of this bot")
            return

        trace: str = traceback.format_exc()
        if len(trace) > 1900:
            trace = trace[-1900:]
        logger.error(msg=trace)
        await ctx.respond(content=f"An error occurred while running the command:\n{trace}")

    @commands.slash_command()
    @commands.guild_only()
    async def list_tracked_users(self, ctx: discord.ApplicationContext):
        if not ctx.author.guild_permissions.administrator and not is_owner(ctx.author.id):
            await ctx.respond(content="You do not have admin permissions")
            return

        users: list = db_cursor.execute(
            "SELECT username FROM PlayersPerGuild WHERE guild_id = ? ORDER BY username COLLATE NOCASE ASC",
            (ctx.guild_id,)).fetchall()
        if not users:
            await ctx.respond("There is currently no users tracked")
            return

        await ctx.respond(content=", ".join(user[0] for user in users))

    @commands.slash_command()
    @commands.guild_only()
    async def set_adjusted_preference(
        self, ctx: discord.ApplicationContext, preference=discord.Option(str, description="", choices=[
            "No adjusted rarity", "No cave constant", "Use cave constant", "Show both"
        ])
        ):
        if not ctx.author.guild_permissions.administrator and not is_owner(ctx.author.id):
            await ctx.respond(content="You do not have admin permissions")
            return

        match preference:
            case "No adjusted rarity":
                _preference = AdjustedPreferences.NONE
            case "No cave constant":
                _preference = AdjustedPreferences.BASE
            case "Use cave constant":
                _preference = AdjustedPreferences.CONSTANT
            case "Show both":
                _preference = AdjustedPreferences.BOTH
            case _:
                _preference = AdjustedPreferences.CONSTANT

        db_cursor.execute(
            """
            INSERT INTO AdjustedPreferencesPerGuild (guild_id, preference)
            VALUES (?, ?)
            ON CONFLICT(guild_id)
                DO UPDATE SET preference = excluded.preference
            """,
            (ctx.guild_id, _preference,)
        )
        db_conn.commit()
        await ctx.respond(content=f"Set adjusted preference to \"{preference}\"")


def setup(_bot: discord.Bot) -> None:
    """
    Expose these commands to the extension system.
    """
    _bot.add_cog(MiscCommands(_bot))
