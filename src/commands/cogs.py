"""
Main file to load and sync commands.
"""

from discord import Bot


def setup_commands(_bot: Bot) -> None:
    _bot.load_extension("commands.main_cogs")
    # _bot.load_extension("commands.misc_cogs")
