"""
Miscellaneous cogs. Put commands in here that are non-essential to the functionality of the bot.
"""

import traceback

from discord.ext import commands
from difflib import get_close_matches

from utils.defs import *
from utils.utils import *

def find_closest_name(ore_name: str) -> str | None:
    symbol_ores_list = ['sigma', 'pi', 'omega', 'lunar omega', 'delta', 'psi', 'infinictrite', 'noopa', 'noo p a']
    number_ores_list = ['combustion system', 'trojan']
    if ore_name.lower() in symbol_ores_list:
        return ['Σ', 'π', 'Ω', 'Lunar Ω', 'Δ', 'ψ', '∞', 'NOO P α', 'NOO P α'][symbol_ores_list.index(ore_name.lower())]
    elif ore_name.lower() in number_ores_list:
        return ['@Combust10n_+_Syst3m', 'TR0J4N'][number_ores_list.index(ore_name.lower())]

    name_list: dict = ALL_ORES.get('Ores', {})
    if not name_list:
        raise ValueError
    
    name_list_lower: dict = { n.lower(): n for n in name_list }
    matches = get_close_matches(ore_name.lower(), name_list_lower.keys(), 1)
    return name_list_lower[matches[0]] if matches else None

# lazy
def get_stuff(ore_name: str, ore_rarity: int) -> list[str, int] | None: 
    ion_multiplier = 1
    tier_name = "Common"
    match ore_name:
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
            elif 7500000 <= ore_rarity <= 15000000:  # exquisite
                ion_multiplier = 45
                tier_name = "Exquisite"
            elif 15000001 <= ore_rarity <= 49999999:  # transcendant
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

    return [tier_name, ion_multiplier]


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

    @commands.slash_command()
    async def ore_info(
        self, ctx: discord.ApplicationContext,
        ore_name: str,
        ore_type = discord.Option(str, "Enter a variant", choices=["Normal", "Ionized", "Spectral"], required=False, default="Normal"),
        cave_type = discord.Option(str, "Enter a cave type", required=False),
    ):
        closest_name: str | None = None
        if ore_name not in ALL_ORES.get("Ores", {}):
            closest_name = find_closest_name(ore_name)
            if not closest_name:
                return await ctx.respond(content=f"Ore name \"{ore_name}\" was not found")
            ore_name = closest_name
        
        if cave_type is not None:
            if cave_type.lower() == "none" or ore_name.lower() == "zanarchium":
                cave_type = None
            elif ore_name.lower() != "zanarchium":
                if not get_nth_word(string=cave_type, n=2):
                    cave_type += " Cave"
                    if cave_type != "nil Cave":
                        cave_type = cave_type.title()

        if cave_type and cave_type not in CAVE_ORES.keys():
            return await ctx.respond(content=f"Cave type \"{cave_type}\" was not found")
        
        base_rarity: int | None = ALL_ORES.get("Ores", {}).get(ore_name)
        if not base_rarity:
            return await ctx.respond(content=f"Ore name \"{ore_name}\" was not found")
        
        is_cave_exclusive: bool = False
        is_nebulova_event: bool = False
        tier: str = ""

        ion_mult: int = 1
        ore_attr: OreAttributes | None = get_ore_attributes(ore_name=ore_name)
        if ore_attr:
            ion_mult = ore_attr.ion_mult
            tier = ore_attr.tier_name
            is_cave_exclusive = ore_attr.is_cave_exclusive
            if ore_attr.cave_type != "Starry Cave" or not cave_type:
                cave_type = ore_attr.cave_type
        else:
            if ore_name == "Agsperum's Charm":
                tier = "Enigmatic"
                ion_mult = 30
            else:
                idk: list[str, int] = get_stuff(ore_name=ore_name, ore_rarity=base_rarity)
                if idk:
                    tier = idk[0]
                    ion_mult = idk[1]
        
        real_cave_type: str | None = cave_type
        if ore_name in CAVE_ORES["Starry Cave"]["ores"] and cave_type:
            if (cave_type == "Gilded Cave" and is_cave_exclusive) or (cave_type != "Starry Cave" and cave_type != "Gilded Cave"):
                is_nebulova_event = True
                real_cave_type = "Starry Cave"
        
        if ore_name == "Black Flame":
            if real_cave_type == "Solar Cave":
                cave_type = "Solar Cave"
            else:
                cave_type = "Darkmatter Cave"
        
        if cave_type and not is_cave_exclusive and cave_type != "Gilded Cave":
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
        if cave_type:
            text += f" (*{cave_type}*)"
        text += f"\nTier: {tier}\n"
        text += f"Rarity: {round(base_rarity):,}\n"
        if cave_type:
            adjusted_rarity_norm = get_ore_rarity(ore_name=ore_name, base_rarity=base_rarity, ore_type=ore_type, cave_type=cave_type, loadout=None, do_adjusted=True, run_nebulova=False)
            if cave_type == "Gilded Cave":
                text += f"Adjusted Rarity (5700): 1/{round(adjusted_rarity_norm * decimal.Decimal(1.88)):,} [CC] | 1/{adjusted_rarity_norm:,}\n"
                adjusted_rarity_salad = get_ore_rarity(ore_name=ore_name, base_rarity=base_rarity, ore_type=ore_type, cave_type=cave_type, loadout="57 Leaf Clover", do_adjusted=True, run_nebulova=False)
                text += f"Adjusted Rarity (57): 1/{round(adjusted_rarity_salad * decimal.Decimal(1.88)):,} [CC] | 1/{adjusted_rarity_salad:,}\n"
            else:
                text += f"Adjusted Rarity: 1/{round(adjusted_rarity_norm * decimal.Decimal(1.88)):,} [CC] | 1/{adjusted_rarity_norm:,}\n"
        
        await ctx.respond(content=text)

def setup(_bot: discord.Bot) -> None:
    """
    Expose these commands to the extension system.
    """
    _bot.add_cog(MiscCommands(_bot))
