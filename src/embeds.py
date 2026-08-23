import config, decimal, discord, aiohttp, utils
from discord import Embed
from defs import AdjustedPreferences, bot, db_cursor, DiscordChannel, logger, OreTiers, TierNames, TIER_NAME_TO_COLOR_HEX, TIER_NAME_TO_TIER_RANK

async def report_permission_warning(guild: discord.Guild, is_global_channel: bool) -> None:
    if guild.owner is None:
        return
    
    # DM the owner of the server to report that we are missing permissions.
    if is_global_channel:
        await guild.owner.send(f"I am unable to send tracker messages in the global channel in the server \"**{guild.name}**.\" I am likely missing permissions to send messages in the global channel you have set. Please make sure I have administrator permissions and that I can send messages in the set global channel.")
    else:
        await guild.owner.send(f"I am unable to send tracker messages in the server \"**{guild.name}**.\" I am likely missing permissions to send messages in the tracker channel you have set. Please make sure I have administrator permissions and that I can send messages in the set tracker channel.")
    
    print(f"Sent a permission warning to server {guild.name} (Guild ID: {guild.id})")
    logger.debug(f"Sent a permission warning to server {guild.name} (Guild ID: {guild.id})")

# Helper function
async def attempt_to_send_to_channel(channel: DiscordChannel, content: str | None = None, embed: discord.Embed | None = None, is_global_channel: bool = False) -> None:
    if not channel.can_send(embed):
        await report_permission_warning(guild=channel.guild, is_global_channel=is_global_channel)
        return

    try:
        await channel.send(content=content, embed=embed)
    except discord.errors.Forbidden: # This probably won't be tripped since the above can_send function will catch it first.
        await report_permission_warning(guild=channel.guild, is_global_channel=is_global_channel)

# this has the same parameters as send_data.
def create_embed(
    # ore data
    ore_name: str,
    ore_rarity: int,  # base rarity, not adjusted
    cave_type: str | None,
    ore_tier: TierNames | str,  # the tier that appears on the track
    ore_type: str,  # normal, ionized, spectral
    event: str,
    world: str | None,
    # user data
    username: str,
    loadout: str,
    blocks_mined: int,
    # misc
    guild_id: int | None = None,
    manual_tracked: bool = False
) -> Embed | None:
    # stax; fix up ore rarity for stuff like nebulova event, or zanarchium being 0 rarity on tracker
    base_rarity: int = utils.get_ore_rarity(ore_name=ore_name, base_rarity=ore_rarity, ore_type=ore_type, cave_type=cave_type,
                                      loadout=loadout, do_adjusted=False, run_nebulova=True)

    embed: discord.Embed = discord.Embed(color=TIER_NAME_TO_COLOR_HEX.get(ore_tier, 0))
    embed.title = f"**{username}** has found {"a spectral " if ore_type == "SPECTRAL" else "an ionized " if ore_type == "IONIZED" else ""}**{ore_name}**{f' (*{cave_type}*)' if cave_type else ''}"

    if world is not None:
        if manual_tracked:
            embed.description = f"[Manual Tracked]\n{world}"
        else:
            embed.description = world

    if cave_type:
        embed.add_field(name="Rarity", value=f"1/{base_rarity:,} in {cave_type}s", inline=True)
    else:
        embed.add_field(name="Rarity", value=f"1/{base_rarity:,}", inline=True)
    embed.add_field(name="Blocks Mined", value=f"{blocks_mined:,}", inline=True)
    embed.add_field(name="Event", value=event, inline=True)
    embed.add_field(name="Loadout", value=loadout, inline=False)

    if cave_type:
        adjusted_preference = db_cursor.execute("SELECT preference FROM AdjustedPreferencesPerGuild WHERE guild_id = ?",
                                                (guild_id,)).fetchone()
        if adjusted_preference:
            adjusted_preference = adjusted_preference[0]
        else:
            adjusted_preference = AdjustedPreferences.BOTH
        if adjusted_preference != AdjustedPreferences.NONE:
            # stax; use run_nebulova = False because base_rarity calculations above already account for it.
            adjusted_rarity: int = utils.get_ore_rarity(ore_name=ore_name, base_rarity=base_rarity, ore_type=ore_type,
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
    if len(embed) > 6000:
        logger.error(msg="[create_embed] Embed was too long!")
        return None

    return embed


async def send_data(
    # ore data
    ore_name: str,
    ore_rarity: int,  # base rarity, not adjusted
    cave_type: str | None,
    ore_tier: TierNames | None,  # the tier that appears on the track
    ore_type: str,  # normal, ionized, spectral
    event: str,
    world: str | None,
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
        logger.error(msg=f"[send_data] Couldn't find a corresponding tier rank for a tier.\nore tier: {ore_tier}\n")
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
        players: list[str] | None = player_dict.get(int(guild_id), None)
        if players is None or len(players) == 0:
            continue
        # stax; use lower() so that people dont have to put exact users. roblox doesnt allow names with different cases but same letters anyways
        # this checks if the username is tracked in this server.
        if username.lower() in [player.lower() for player in players]:
            tracker_channel: DiscordChannel = await bot.get_or_fetch(object_type=discord.TextChannel, object_id=tracker_channel_id)
            if tracker_channel is None:
                logger.error(msg=f"[send_data] Couldn't find tracker channel {tracker_channel_id} in guild id {guild_id}!")
                # TODO: stax; remove the channel from the database if its not found.
                continue

            embed: discord.Embed | None = create_embed(ore_name=ore_name, ore_rarity=ore_rarity, cave_type=cave_type,
                                                ore_tier=ore_tier, ore_type=ore_type, event=event, world=world,
                                                username=username, loadout=loadout, blocks_mined=blocks_mined,
                                                guild_id=guild_id, manual_tracked=manual_tracked)
            if embed is None:
                continue

            user_pings: list = db_cursor.execute(
                "SELECT user_id, globals_only FROM PingsPerUsername WHERE guild_id = ? AND username = ?",
                (guild_id, username,)).fetchall()

            ping_ids = []
            for user_id, globals_only in user_pings:
                if globals_only and not is_global:
                    continue
                ping_ids.append(user_id)
            pings = "".join([f"<@{uid}>" for uid in ping_ids])

            if is_global:
                # FIXME: stax; make this look better.
                global_message: list[str] | str = db_cursor.execute(
                    "SELECT message from GlobalMessagePerGuild WHERE guild_id = ?", (guild_id,)).fetchone()
                if global_message:
                    global_message = global_message[0]
                else:
                    global_message = ""

                if guild_id == 1248099267449458688:
                    ping = utils.get_global_role_ping(ore_name=ore_name.lower(), ore_rarity=ore_rarity, ore_rank=tier_rank, ore_type=ore_type, cave_type=cave_type)
                    global_message = f"{ping}{global_message}"
                elif guild_id == 1505320837916659783:
                    base_rarity: int = utils.get_ore_rarity(ore_name=ore_name, base_rarity=ore_rarity, ore_type=ore_type, cave_type=cave_type,
                                      loadout=loadout, do_adjusted=False, run_nebulova=True)
                    adjusted_rarity: int = 0
                    if cave_type is not None:
                        adjusted_rarity = utils.get_ore_rarity(ore_name=ore_name, base_rarity=base_rarity, ore_type=ore_type,
                                                  cave_type=cave_type, loadout=loadout, do_adjusted=True,
                                                  run_nebulova=False)
                    if tier_rank < OreTiers.OTHERWORLDLY and ore_rarity < 2_000_000_000 and not (cave_type is not None and adjusted_rarity >= 2_000_000_000):
                        global_message = ""

                if ping_ids:
                    await attempt_to_send_to_channel(channel=tracker_channel, content=f"{global_message}\n{pings}", embed=embed)
                else:
                    await attempt_to_send_to_channel(channel=tracker_channel, content=global_message, embed=embed)

                if global_channel_id is not None:
                    global_channel: DiscordChannel = bot.get_or_fetch(object_type=discord.TextChannel, object_id=global_channel_id)
                    if global_channel is None:
                        logger.error(msg=f"[send_data] Couldn't find global channel {global_channel_id} in guild id {guild_id}!")
                        # TODO: stax; remove the channel from the database if its not found.
                        continue
                    
                    await attempt_to_send_to_channel(channel=global_channel, embed=embed, is_global_channel=True)
            else:
                if ping_ids:
                    await attempt_to_send_to_channel(channel=tracker_channel, content=pings, embed=embed)
                else:
                    await attempt_to_send_to_channel(channel=tracker_channel, embed=embed)

    if not config.DEV_MODE:
        # stax; send to channels it needs to be sent to.
        embed: discord.Embed | None = create_embed(ore_name=ore_name, ore_rarity=ore_rarity, cave_type=cave_type,
                                                    ore_tier=ore_tier, ore_type=ore_type, event=event, world=world,
                                                    username=username, loadout=loadout, blocks_mined=blocks_mined,
                                                    guild_id=None, manual_tracked=False)
        if embed is None:
            logger.error("[send_data] Missing embed, can't send anything!")
            return
        
        base_rarity: int = utils.get_ore_rarity(ore_name=ore_name, base_rarity=ore_rarity, ore_type=ore_type, cave_type=cave_type,
                                        loadout=loadout, do_adjusted=False, run_nebulova=True)
        adjusted_rarity: int = round(utils.get_ore_rarity(ore_name, base_rarity, ore_type, cave_type, loadout, do_adjusted=True,
                                        run_nebulova=False) * 1.88)
        if is_global:
            cat_global_channel: DiscordChannel = bot.get_or_fetch(object_type=discord.TextChannel, object_id=1306083504370618470)
            if cat_global_channel:
                await cat_global_channel.send(embed=embed)
            wdor_global_channel: DiscordChannel = bot.get_channel(object_type=discord.TextChannel, object_id=1508240892933443604)
            if wdor_global_channel:
                await wdor_global_channel.send(embed=embed)

        if blocks_mined <= 5000000:
            cat_beginner_channel: DiscordChannel = bot.get_channel(object_type=discord.TextChannel, object_id=1311792395414667304)
            if cat_beginner_channel and embed:
                if is_global or base_rarity >= 5_000_000_000:
                    await cat_beginner_channel.send(content="<@&1455083226828902566>", embed=embed)
                else:
                    await cat_beginner_channel.send(embed=embed)

            if config.WEBHOOK_LINK is not None:
                async with aiohttp.ClientSession() as session: # sending to glaggleland
                    webhook = discord.Webhook.from_url(
                        url=config.WEBHOOK_LINK,
                        session=session,
                    )
                    if is_global or base_rarity >= 5_000_000_000:
                        await webhook.send("<@&1326276408087023638>", embed=embed)
                    else:
                        await webhook.send(embed=embed)

        cat_rare_ore_tracker_channel: DiscordChannel = bot.get_or_fetch(object_type=discord.TextChannel, object_id=1407955712209977415)
        if cat_rare_ore_tracker_channel is not None:
            if cave_type is not None and adjusted_rarity >= 100_000_000_000:
                await cat_rare_ore_tracker_channel.send("<@&1416256696384487525>", embed=embed)
            elif tier_rank == OreTiers.IMAGINARY and ore_type != "NORMAL":
                await cat_rare_ore_tracker_channel.send("<@&1466449671428767895> <@&1416256696384487525>", embed=embed)
            elif tier_rank == OreTiers.IMAGINARY:
                await cat_rare_ore_tracker_channel.send("<@&1466449671428767895>", embed=embed)
            elif base_rarity >= 50_000_000_000:
                await cat_rare_ore_tracker_channel.send("<@&1416256696384487525>", embed=embed)
