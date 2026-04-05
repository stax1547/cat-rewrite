import decimal
import os

import aiohttp
from discord import Embed

from utils.defs import *
from utils.utils import get_ore_rarity


# this has the same parameters as send_data.
def create_embed(
    # ore data
    ore_name: str,
    ore_rarity: int,  # base rarity, not adjusted
    cave_type: str | None,
    ore_tier: str,  # the tier that appears on the track
    ore_type: str,  # normal, ionized, spectral
    event: str,
    world: str,
    # user data
    username: str,
    loadout: str,
    blocks_mined: int,
    # misc
    guild_id: int = None,
    manual_tracked: bool = False
) -> Embed | None:
    # stax; fix up ore rarity for stuff like nebulova event, or zanarchium being 0 rarity on tracker
    base_rarity: int = get_ore_rarity(ore_name=ore_name, base_rarity=ore_rarity, ore_type=ore_type, cave_type=cave_type,
                                      loadout=loadout, do_adjusted=False, run_nebulova=True)

    embed: discord.Embed = discord.Embed(color=TIER_NAME_TO_COLOR_HEX.get(ore_tier, 0))
    embed.title = f"**{username}** has found {"a spectral " if ore_type == "SPECTRAL" else "an ionized " if ore_type == "IONIZED" else ""}**{ore_name}**{f' (*{cave_type}*)' if cave_type else ''}"

    if manual_tracked:
        embed.description = f"[Manual Tracked]\n{world}"
    else:
        embed.description = world

    if cave_type:
        embed.add_field(name="Rarity", value=f"1/{ore_rarity:,} in {cave_type}s", inline=True)
    else:
        embed.add_field(name="Rarity", value=f"1/{ore_rarity:,}", inline=True)
    embed.add_field(name="Blocks Mined", value=f"{blocks_mined:,}", inline=True)
    embed.add_field(name="Event", value=event, inline=True)
    embed.add_field(name="Loadout", value=loadout, inline=False)

    if cave_type:
        adjusted_preference = db_cursor.execute("SELECT preference FROM AdjustedPreferencesPerGuild WHERE guild_id = ?",
                                                (guild_id,)).fetchone()
        print(adjusted_preference)
        if adjusted_preference:
            adjusted_preference = adjusted_preference[0]
        else:
            adjusted_preference = AdjustedPreferences.BOTH
        if adjusted_preference != AdjustedPreferences.NONE:
            # stax; use run_nebulova = False because base_rarity calculations above already account for it.
            adjusted_rarity: int = get_ore_rarity(ore_name=ore_name, base_rarity=base_rarity, ore_type=ore_type,
                                                  cave_type=cave_type, loadout=loadout, do_adjusted=True,
                                                  run_nebulova=False)
            adjusted_rarity_cc = round(adjusted_rarity * decimal.Decimal(1.88))
            match adjusted_preference:
                case AdjustedPreferences.BASE:
                    embed.add_field(name="Adjusted Rarity", value=f"1/{adjusted_rarity:,}", inline=False)
                case AdjustedPreferences.CONSTANT:
                    embed.add_field(name="Adjusted Rarity", value=f"1/{adjusted_rarity_cc:,}", inline=False)
                case AdjustedPreferences.BOTH:
                    embed.add_field(name="Adjusted Rarity",
                                    value=f"1/{adjusted_rarity_cc:,} [CC] | 1/{adjusted_rarity:,}")

    # stax; prevent the bot from sending something that is too long
    # this is probably never going to be true (?), but i like to be safe
    if len(embed) > 6000:
        logger.error(msg="embed was too long!")
        return None

    return embed


async def send_data(
    # ore data
    ore_name: str,
    ore_rarity: int,  # base rarity, not adjusted
    cave_type: str | None,
    ore_tier: str,  # the tier that appears on the track
    ore_type: str,  # normal, ionized, spectral
    event: str,
    world: str,
    # user data
    username: str,
    loadout: str,
    blocks_mined: int,
    # misc
    manual_tracked: bool = False
) -> None:

    tier_rank: OreTiers = TIER_NAME_TO_TIER_RANK.get(ore_tier, -1)
    if tier_rank == -1:
        # stax; Don't skip the track if this is true, as we can still track it (it will have a white color on the tracker)
        logger.error(msg=f"couldn't find a corresponding tier rank for a tier.\nore tier: {ore_tier}\n")
    is_global: bool = tier_rank == -1 or tier_rank >= OreTiers.UNFATHOMABLE or (
            tier_rank >= OreTiers.ENIGMATIC and ore_type == "IONIZED") or (
                              tier_rank >= OreTiers.TRANSCENDENT and ore_type == "SPECTRAL")

    channel_data: list[tuple[int, int, int]] = db_cursor.execute(
        """
        SELECT guild_id, tracker_channel_id, global_channel_id
        FROM ChannelsPerGuild
        """
    ).fetchall()

    # stax; populate our dictionary with the usernames and key it by guild id so we dont do queries for each guild id
    player_dict: dict[int, list[str]] = {}
    player_data: list[tuple[int, str]] = db_cursor.execute("SELECT guild_id, username from PlayersPerGuild").fetchall()
    for guild_id, _username in player_data:
        player_dict.setdefault(guild_id, []).append(_username)

    for guild_id, tracker_channel_id, global_channel_id in channel_data:
        players: list[str] = player_dict.get(int(guild_id), [])
        if not players or not len(players):
            continue
        # stax; use lower() so that people dont have to put exact users. roblox doesnt allow names with different cases but same letters anyways
        # this checks if the username is tracked in this server.
        if username.lower() in [player.lower() for player in players]:
            tracker_channel: discord.TextChannel = bot.get_channel(tracker_channel_id)
            if not tracker_channel:
                logger.error(msg=f"could not find tracker channel {tracker_channel_id} in {guild_id}!")
                # TODO: stax; remove the channel from the database if its not found.
                continue

            embed: discord.Embed = create_embed(ore_name=ore_name, ore_rarity=ore_rarity, cave_type=cave_type,
                                                ore_tier=ore_tier, ore_type=ore_type, event=event, world=world,
                                                username=username, loadout=loadout, blocks_mined=blocks_mined,
                                                guild_id=guild_id, manual_tracked=manual_tracked)
            if not embed:
                continue

            user_pings: list = db_cursor.execute(
                "SELECT user_id FROM PingsPerUsername WHERE guild_id = ? AND username = ?",
                (guild_id, username,)).fetchall()

            if is_global:
                # FIXME: stax; make this look better.
                global_message: list[str] | str = db_cursor.execute(
                    "SELECT message from GlobalMessagePerGuild WHERE guild_id = ?", (guild_id,)).fetchone()
                if global_message:
                    global_message = global_message[0]
                else:
                    global_message = ""

                if len(user_pings) > 0:
                    pings: str = "".join([f"<@{uid[0]}>" for uid in user_pings])
                    await tracker_channel.send(content=f"{global_message}\n{pings}", embed=embed)
                else:
                    await tracker_channel.send(content=global_message, embed=embed)

                if global_channel_id:
                    global_channel: discord.TextChannel = bot.get_channel(global_channel_id)
                    if not global_channel:
                        logger.log(level=logging.ERROR,
                                   objects=f"could not find global channel {global_channel} in {guild_id}!")
                        # TODO: stax; remove the channel from the database if its not found.
                        continue

                    await global_channel.send(embed=embed)
            else:
                if len(user_pings) > 0:
                    pings: str = "".join([f"<@{uid[0]}>" for uid in user_pings])
                    await tracker_channel.send(content=pings, embed=embed)
                else:
                    await tracker_channel.send(embed=embed)

    # stax; send to channels it needs to be sent to.
    embed: discord.Embed = create_embed(ore_name=ore_name, ore_rarity=ore_rarity, cave_type=cave_type,
                                                ore_tier=ore_tier, ore_type=ore_type, event=event, world=world,
                                                username=username, loadout=loadout, blocks_mined=blocks_mined,
                                                guild_id=None, manual_tracked=False)
    if not embed:
        return
    
    if is_global and not manual_tracked:
        cat_global_channel: discord.TextChannel = bot.get_channel(1306083504370618470)
        if cat_global_channel:
                await cat_global_channel.send(embed=embed)

    base_rarity: int = get_ore_rarity(ore_name=ore_name, base_rarity=ore_rarity, ore_type=ore_type, cave_type=cave_type,
                                      loadout=loadout, do_adjusted=False, run_nebulova=True)
    if blocks_mined <= 5000000:
        cat_beginner_channel: discord.TextChannel = bot.get_channel(1311792395414667304)
        if cat_beginner_channel and embed:
            if is_global or base_rarity >= 5_000_000_000:
                await cat_beginner_channel.send(content="<@&1455083226828902566>", embed=embed)
            else:
                await cat_beginner_channel.send(embed=embed)

        async with aiohttp.ClientSession() as session:  # sending to glaggleland
            webhook = discord.Webhook.from_url(
                url=os.getenv("GLAGGLELAND_WEBHOOK"),
                session=session,
            )
            if is_global == True or base_rarity >= 5_000_000_000:
                await webhook.send("<@&1326276408087023638>", embed=embed)
            else:
                await webhook.send(embed=embed)

    adjusted_rarity = get_ore_rarity(ore_name, base_rarity, ore_type, cave_type, loadout, do_adjusted=True,
                                     run_nebulova=False) * decimal.Decimal(1.88)
    cat_rare_ore_tracker_channel = bot.get_channel(1407955712209977415)
    if cave_type is not None and adjusted_rarity >= 100_000_000_000:
        await cat_rare_ore_tracker_channel.send("<@&1416256696384487525>", embed=embed)
    elif tier_rank == OreTiers.IMAGINARY and ore_type != "NORMAL":
        await cat_rare_ore_tracker_channel.send("<@&1466449671428767895> <@&1416256696384487525>", embed=embed)
    elif tier_rank == OreTiers.IMAGINARY:
        await cat_rare_ore_tracker_channel.send("<@&1466449671428767895>", embed=embed)
    elif base_rarity >= 50_000_000_000:
        await cat_rare_ore_tracker_channel.send("<@&1416256696384487525>", embed=embed)
