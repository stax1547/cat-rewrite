"""
Miscellaneous cogs. Put commands in here that are non-essential to the functionality of the bot.
"""

import decimal, discord, utils

from discord.ext import commands
from defs import AdjustedPreferences, ALL_ORES, CAVE_ORES, db_conn, db_cursor, OreTypes

def get_data_for_ore(ore_name: str, ore_rarity: int) -> utils.OreAttributes | None: 
    tier_name: str = "Common"
    ion_multiplier: int = 1

    match ore_name:
        case "agsperum's charm":
            ion_multiplier = 30
            tier_name = "Enigmatic"
        case "protoflare":
            ion_multiplier = 45
            tier_name = "Exquisite"
        case "superunobtainium":
            ion_multiplier = 60
            tier_name = "Mythic"
        case "zanarchium":
            ion_multiplier = 10
            tier_name = "Zenith"
        case "corrupt god tycoon crystal" | "stable minicores" | "paste crystal" | "noo p ω" | "delusory bubblegram"\
            | "illusionary bubblegum" | "cake ore" | "random" | "vantachaos" | "acrimoney" | "360-brat integer limit"\
            | "oil crystal" | "iridophyte" | "dynamo of fates" | "fantamalgamation" | "vitriol crystal" | "absolute everything"\
            | "the sun" | "slaylarius":
            ion_multiplier = 10
            tier_name = "Exclusive"
        case "aurora polaris":
            ion_multiplier = 30
            tier_name = "Enigmatic"
        case "electrolyx":
            ion_multiplier = 45
            tier_name = "Exquisite"
        case "eggsquisite":
            ion_multiplier = 45
            tier_name = "Exquisite"
        case _:
            if ore_rarity <= 999:  # common
                ion_multiplier = 110
                tier_name = "Common"
            elif 1000 <= ore_rarity <= 9999:  # uncommon
                ion_multiplier = 100
                tier_name = "Uncommon"
            elif 10000 <= ore_rarity <= 29999:  # rare
                ion_multiplier = 90
                tier_name = "Rare"
            elif 30000 <= ore_rarity <= 89000:  # master
                ion_multiplier = 80
                tier_name = "Master"
            elif 89001 <= ore_rarity <= 499999:  # surreal
                ion_multiplier = 70
                tier_name = "Surreal"
            elif 500000 <= ore_rarity <= 999999:  # mythic
                ion_multiplier = 60
                tier_name = "Mythic"
            elif 1000000 <= ore_rarity <= 7499999:  # exotic
                ion_multiplier = 50
                tier_name = "Exotic" 
            elif 7500000 <= ore_rarity <= 14999999:  # exquisite
                ion_multiplier = 45
                tier_name = "Exquisite"
            elif 15000000 <= ore_rarity <= 49999999:  # transcendant
                ion_multiplier = 40
                tier_name = "Transcendent"
            elif 50000000 <= ore_rarity <= 99999999:  # enigmatic
                ion_multiplier = 30
                tier_name = "Enigmatic"
            elif 100000000 <= ore_rarity <= 774999999:  # unfath
                ion_multiplier = 20
                tier_name = "Unfathomable"
            elif 775000000 <= ore_rarity <= 10000000000 :  # ow
                ion_multiplier = 15
                tier_name = "Otherworldly"
            elif ore_rarity >= 20000000000: # imagine
                ion_multiplier = 15
                tier_name = "Imaginary"

    if ion_multiplier == 1:
        return None

    ore_attributes: utils.OreAttributes = utils.OreAttributes()
    ore_attributes.ion_mult = ion_multiplier
    ore_attributes.tier_name = tier_name
    return ore_attributes

class MiscCommands(commands.Cog):
    def __init__(self, _bot: discord.Bot):
        self.bot = _bot

    async def cog_command_error(self, ctx: discord.ApplicationContext, error: commands.CommandError):
        await utils.handle_error(ctx=ctx, error=error) 

    @commands.slash_command(description="List all usernames tracked in this server.")
    @commands.guild_only()
    @commands.check(utils.permissions_check)
    async def list_tracked_users(self, ctx: discord.ApplicationContext):
        users: list = db_cursor.execute(
            "SELECT username FROM PlayersPerGuild WHERE guild_id = ? ORDER BY username COLLATE NOCASE ASC",
            (ctx.guild_id,)).fetchall()
        if not users:
            await ctx.respond("There are currently no users tracked.")
            return

        await ctx.respond(content=", ".join(user[0] for user in users))

    @commands.slash_command(description="Set what should be used for the formatting on adjusted rarity.")
    @commands.guild_only()
    @discord.commands.option("preference", str, description="Adjusted rarity setting", choices=["No adjusted rarity", "No cave constant", "Use cave constant", "Show both"])
    @commands.check(utils.permissions_check)
    async def set_adjusted_preference(self, ctx: discord.ApplicationContext, preference: str):
        match preference:
            case "No adjusted rarity":
                _preference = AdjustedPreferences.NONE
            case "No cave constant":
                _preference = AdjustedPreferences.BASE
            case "Use cave constant":
                _preference = AdjustedPreferences.CONSTANT
            case "Show both":
                _preference = AdjustedPreferences.BOTH
            case _: # This will never be hit unless I make a typo in the choices...
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
        await ctx.respond(content=f"Set adjusted preference to \"{preference}\".")

    @commands.slash_command(
            description="Provides info for an ore given the parameters.",
            integration_types={ discord.IntegrationType.user_install, discord.IntegrationType.guild_install } # Allow this to be used outside of servers where the bot is.
        )
    @commands.cooldown(rate=3, per=5, type=commands.BucketType.user)
    @discord.commands.option("ore_name", str, description="The name of the ore you want the info of", autocomplete=utils.ore_name_autocomplete)
    @discord.commands.option("ore_type", str, description="The variant of the ore", choices=["Normal", "Ionized", "Spectral"], required=False, default="Normal")
    @discord.commands.option("cave_type", str, description="The cave type of the ore. Not required for cave exclusives", autocomplete=utils.cave_type_autocomplete, required=False, default=None)
    async def ore_info(
        self, ctx: discord.ApplicationContext,
        ore_name: str,
        ore_type: str = "Normal",
        cave_type: str = None,
    ):        
        if cave_type is not None and (cave_type.lower() == "none" or ore_name.lower() == "zanarchium"):
            cave_type = None

        # Fix up cave type
        if cave_type is not None and utils.get_nth_word(cave_type, 2) is None:
            cave_type = f"{cave_type} Cave"

        if cave_type is not None and cave_type not in CAVE_ORES.keys():
            return await ctx.respond(content=f"Cave type \"{cave_type}\" was not found")
        
        base_rarity: int | None = ALL_ORES.get("Ores", {}).get(ore_name)
        if base_rarity is None:
            return await ctx.respond(content=f"Ore name \"{ore_name}\" was not found")
        
        is_cave_exclusive: bool = False
        is_nebulova_event: bool = False
        tier: str = ""

        ion_mult: int = 1
        ore_attr: utils.OreAttributes | None = utils.get_ore_attributes(ore_name=ore_name)
        if ore_attr is not None:
            ion_mult = ore_attr.ion_mult
            tier = ore_attr.tier_name
            is_cave_exclusive = ore_attr.is_cave_exclusive
            if ore_attr.cave_type != "Starry Cave" or cave_type is None:
                cave_type = ore_attr.cave_type
        else:
            ore_data: utils.OreAttributes | None = get_data_for_ore(ore_name=ore_name.lower(), ore_rarity=base_rarity)
            if ore_data is not None:
                tier = ore_data.tier_name
                ion_mult = ore_data.ion_mult
        
        real_cave_type: str | None = cave_type
        if ore_name in CAVE_ORES["Starry Cave"]["ores"] and cave_type is not None:
            if (cave_type == "Gilded Cave" and is_cave_exclusive) or (cave_type != "Starry Cave" and cave_type != "Gilded Cave"):
                is_nebulova_event = True
                real_cave_type = "Starry Cave"
        
        if ore_name == "Black Flame":
            if real_cave_type == "Solar Cave":
                cave_type = "Solar Cave"
            else:
                cave_type = "Darkmatter Cave"
        
        if cave_type is not None and not is_cave_exclusive and cave_type != "Gilded Cave":
            base_rarity = CAVE_ORES[real_cave_type]["ores"][ore_name][OreTypes.NORMAL] # leave variant multipliers to below
        
        if ore_type == "Spectral":
            base_rarity *= ion_mult * 15
        elif ore_type == "Ionized":
            base_rarity *= ion_mult
        
        if is_nebulova_event:
            base_rarity *= 3
        elif cave_type == "Gilded Cave" and not is_cave_exclusive and ore_name != "Gold":
            base_rarity *= 2.5
        
        # IM TOO LAZY TO MAKE EMBEDS RN
        text = ""
        if ore_type != "Normal":
            text += f"{ore_type} "
        text += f"{ore_name}"
        if cave_type is not None:
            text += f" (*{cave_type}*)"
        text += f"\nTier: {tier}\n"
        text += f"Rarity: {round(base_rarity):,}\n"
        if cave_type is not None:
            adjusted_rarity_norm = utils.get_ore_rarity(ore_name=ore_name, base_rarity=base_rarity, ore_type=ore_type, cave_type=cave_type, loadout=None, do_adjusted=True, run_nebulova=False)
            if cave_type == "Gilded Cave":
                text += f"Adjusted Rarity (5700): 1/{round(adjusted_rarity_norm * decimal.Decimal(1.88)):,} [CC] | 1/{adjusted_rarity_norm:,}\n"
                adjusted_rarity_100_leaf = utils.get_ore_rarity(ore_name=ore_name, base_rarity=base_rarity, ore_type=ore_type, cave_type=cave_type, loadout="100 Leaf Clover", do_adjusted=True, run_nebulova=False)
                text += f"Adjusted Rarity (100): 1/{round(adjusted_rarity_100_leaf * decimal.Decimal(1.88)):,} [CC] | 1/{adjusted_rarity_100_leaf:,}\n"
                adjusted_rarity_salad = utils.get_ore_rarity(ore_name=ore_name, base_rarity=base_rarity, ore_type=ore_type, cave_type=cave_type, loadout="57 Leaf Clover", do_adjusted=True, run_nebulova=False)
                text += f"Adjusted Rarity (57): 1/{round(adjusted_rarity_salad * decimal.Decimal(1.88)):,} [CC] | 1/{adjusted_rarity_salad:,}\n"
            else:
                text += f"Adjusted Rarity: 1/{round(adjusted_rarity_norm * decimal.Decimal(1.88)):,} [CC] | 1/{adjusted_rarity_norm:,}\n"
        
        await ctx.respond(content=text)

def setup(_bot: discord.Bot) -> None:
    """
    Expose these commands to the extension system.
    """
    _bot.add_cog(MiscCommands(_bot))
