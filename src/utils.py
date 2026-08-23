import config, decimal, discord, difflib
from defs import ALL_ORES, bot, CAVE_ORES, OreTiers, ORE_TYPE_TO_RANK, PermissionLevel, TierNames 

class OreAttributes:
    ion_mult: int = 0
    tier_name: str = ""
    cave_type: str | None = None
    is_cave_exclusive: bool = False

# TODO: rewrite this function
def get_ore_attributes(ore_name: str) -> OreAttributes | None:
    """
    Returns the attributes for an ore based on the ore's name.
    If the ore name passed in is a cave exclusive ore, give back ore attributes about it.
    Currently, these attributes only contain the cave type that the ore spawns in.
    """
    ore_name = ore_name.lower()

    # allows for mass changing of multipliers
    common: tuple[int, TierNames] = (110, TierNames.COMMON)
    uncommon: tuple[int, TierNames] = (100, TierNames.UNCOMMON)
    rare: tuple[int, TierNames] = (90, TierNames.RARE)
    master: tuple[int, TierNames] = (80, TierNames.MASTER)
    surreal: tuple[int, TierNames] = (70, TierNames.SURREAL)
    mythic: tuple[int, TierNames] = (60, TierNames.MYTHIC)
    exotic: tuple[int, TierNames] = (50, TierNames.EXOTIC)
    exquisite: tuple[int, TierNames] = (45, TierNames.EXQUISITE)
    transcendent: tuple[int, TierNames] = (40, TierNames.TRANSCENDENT)
    enigmatic: tuple[int, TierNames] = (30, TierNames.ENIGMATIC)
    unfathomable: tuple[int, TierNames] = (20, TierNames.UNFATHOMABLE)
    otherworldly: tuple[int, TierNames] = (15, TierNames.OTHERWORLDLY)

    # format : ion multiplier, tier name, cave type
    cave_exclusives = {
        "cryotic": [mythic[0], mythic[1], "Frozen Cave"],
        "altovite": [transcendent[0], transcendent[1], "Frozen Cave"],
        "cerlustrium": [enigmatic[0], enigmatic[1], "Frozen Cave"],
        "intoxium": [surreal[0], surreal[1], "Elemental Cave"],
        "hallowed prism": [transcendent[0], transcendent[1], "Elemental Cave"],
        "machina": [otherworldly[0], otherworldly[1], "Divine Cave"],
        "π": [enigmatic[0], enigmatic[1], "Prismatic Cave"],
        "ambrosia": [exquisite[0], exquisite[1], "Gilded Cave"],
        "hyperheated quasar": [enigmatic[0], enigmatic[1], "Gilded Cave"],
        "ophanim": [transcendent[0], transcendent[1], "Gilded Cave"],
        "solace": [unfathomable[0], unfathomable[1], "Gilded Cave"],
        "exdeus": [unfathomable[0], unfathomable[1], "Unstable Cave"],
        "cygnus": [enigmatic[0], enigmatic[1], "Galactic Cave"],
        "observatorium": [otherworldly[0], otherworldly[1], "Enchanted Cave"],
        "lavortia": [transcendent[0], transcendent[1], "Luminous Cave"],
        "lunarian": [exquisite[0], exquisite[1], "Nightfall Cave"],
        "lunar coronium": [exotic[0], exotic[1], "Radioactive Cave"],
        "lunar neptunium": [exotic[0], exotic[1], "Radioactive Cave"],
        "ascended flare": [transcendent[0], transcendent[1], "Magmatic Cave"],
        "lunar gargantium": [transcendent[0], transcendent[1], "Magmatic Cave"],
        "lunar coronal flare": [enigmatic[0], enigmatic[1], "Magmatic Cave"],
        "actinium": [mythic[0], mythic[1], "Radioactive Cave"],
        "surgium": [exquisite[0], exquisite[1], "Radioactive Cave"],
        "lunar lawrencium": [transcendent[0], transcendent[1], "Radioactive Cave"],
        "oganesson": [enigmatic[0], enigmatic[1], "Radioactive Cave"],
        "lunar galaxite": [master[0], master[1], "Interstellar Cave"],
        "tektite": [master[0], master[1], "Interstellar Cave"],
        "lunar pulsar crystal": [exotic[0], exotic[1], "Interstellar Cave"],
        "lunar andromidium": [transcendent[0], transcendent[1], "Interstellar Cave"],
        "r136a1": [transcendent[0], transcendent[1], "Interstellar Cave"],
        "lunar hr 5171 a": [enigmatic[0], enigmatic[1], "Interstellar Cave"],
        "hd 160529": [enigmatic[0], enigmatic[1], "Interstellar Cave"],
        "laniakea supercluster": [unfathomable[0], unfathomable[1], "Interstellar Cave"],
        "accesinite": [enigmatic[0], enigmatic[1], "nil Cave"],
        "genuinium": [enigmatic[0], enigmatic[1], "nil Cave"],
        "fire crystal": [enigmatic[0], enigmatic[1], "nil Cave"],
        "pandorite": [enigmatic[0], enigmatic[1], "nil Cave"],
        "nilnal": [otherworldly[0], otherworldly[1], "nil Cave"],
        "blood lunarian": [exquisite[0], exquisite[1], "Soulseek Cave"],
        "bathophobia": [transcendent[0], transcendent[1], "Fractured Cave"],
        "aurora polaris": [enigmatic[0], enigmatic[1], None],
        "asterium": [exotic[0], exotic[1], "Enchanted Cave"],
        "empress of light": [unfathomable[0], unfathomable[1], "Geode Cave"],
        "drusentyl": [exquisite[0], exquisite[1], "Geode Cave"],
        "teslarium": [exotic[0], exotic[1], "Metallic Cave"],
        "void reaver": [enigmatic[0], enigmatic[1], "Void Cave"],
        "reflectix": [master[0], master[1], "Metallic Cave"],
        "divinessence": [surreal[0], surreal[1], "Divine Cave"],
        "amalgrim": [transcendent[0], transcendent[1], "Soulseek Cave"],
        "heretic's cage": [enigmatic[0], enigmatic[1], "Soulseek Cave"],
        "lovestruck": [exquisite[0], exquisite[1], "Heartstring Cave"],
        "amorisene": [enigmatic[0], enigmatic[1], "Heartstring Cave"],
        "cursed flesh": [transcendent[0], transcendent[1], "Fractured Cave"],
        "draugur": [transcendent[0], transcendent[1], "Fractured Cave"],
        "celebration": [exotic[0], exotic[1], "Firework Cave"],
        "opal": [surreal[0], surreal[1], "Prismatic Cave"],
        "paste crystal": [10, "Exclusive", "feebium Cave"],
        "duamension": [master[0], master[1], "Bichromatic Cave"],
        "dualisplite": [surreal[0], surreal[1], "Bichromatic Cave"],
        "varonela": [exotic[0], exotic[1], "Bichromatic Cave"],
        "arcanicium": [exotic[0], exotic[1], "Bichromatic Cave"],
        "altair": [exquisite[0], exquisite[1], "Bichromatic Cave"],
        "@combust10n_+_syst3m": [exquisite[0], exquisite[1], "Bichromatic Cave"],
        "fatennial": [transcendent[0], transcendent[1], "Bichromatic Cave"],
        "amaranthine": [transcendent[0], transcendent[1], "Bichromatic Cave"],
        "sword waltz": [enigmatic[0], enigmatic[1], "Bichromatic Cave"],
        "thermazine": [unfathomable[0], unfathomable[1], "Bichromatic Cave"],
        "sparkletize": [rare[0], rare[1], "Starry Cave"],
        "astrocase": [master[0], master[1], "Starry Cave"],
        "constellatrix": [surreal[0], surreal[1], "Starry Cave"],
        "heliotropic fracture": [exotic[0], exotic[1], "Starry Cave"],
        "spaceshatter": [exquisite[0], exquisite[1], "Starry Cave"],
        "nebula tempest": [transcendent[0], transcendent[1], "Starry Cave"],
        "lumenyl": [transcendent[0], transcendent[1], "Starry Cave"],
        "astraea": [enigmatic[0], enigmatic[1], "Starry Cave"],
        "aetherion": [enigmatic[0], enigmatic[1], "Starry Cave"],
        "syderea": [otherworldly[0], otherworldly[1], "Starry Cave"],
        "hexagonyl": [rare[0], rare[1], "Matrix Cave"],
        "momentum": [master[0], master[1], "Matrix Cave"],
        "synthetyl": [exotic[0], exotic[1], "Matrix Cave"],
        "4fa208": [exquisite[0], exquisite[1], "Matrix Cave"],
        "f24d43": [exquisite[0], exquisite[1], "Matrix Cave"],
        "geometric quadrant": [transcendent[0], transcendent[1], "Matrix Cave"],
        "geometrix": [enigmatic[0], enigmatic[1], "Matrix Cave"],
        "low.hp": [unfathomable[0], unfathomable[1], "Matrix Cave"],
        "dichromite": [uncommon[0], uncommon[1], "Monoprismatic Cave"],
        "vibrantasia": [master[0], master[1], "Monoprismatic Cave"],
        "prismator": [mythic[0], mythic[1], "Monoprismatic Cave"],
        "anulus": [exotic[0], exotic[1], "Monoprismatic Cave"],
        "hypnosia": [exquisite[0], exquisite[1], "Monoprismatic Cave"],
        "iridistar": [exquisite[0], exquisite[1], "Monoprismatic Cave"],
        "finalitium": [transcendent[0], transcendent[1], "Monoprismatic Cave"],
        "canivesium": [transcendent[0], transcendent[1], "Monoprismatic Cave"],
        "illusorium": [enigmatic[0], enigmatic[1], "Monoprismatic Cave"],
        "collapse": [enigmatic[0], enigmatic[1], "Monoprismatic Cave"],
        "universal collapse": [otherworldly[0], otherworldly[1], "Monoprismatic Cave"],
        "ampersite": [uncommon[0], uncommon[1], "Voltaic Cave"],
        "shockpad": [rare[0], rare[1], "Voltaic Cave"],
        "plasmos": [master[0], master[1], "Voltaic Cave"],
        "hyposhock": [surreal[0], surreal[1], "Voltaic Cave"],
        "electricore": [exotic[0], exotic[1], "Voltaic Cave"],
        "pariluxem": [exotic[0], exotic[1], "Voltaic Cave"],
        "corruptryx": [exotic[0], exotic[1], "Voltaic Cave"],
        "valenarium": [exquisite[0], exquisite[1], "Voltaic Cave"],
        "luminosaic": [transcendent[0], transcendent[1], "Voltaic Cave"],
        "roundabout": [transcendent[0], transcendent[1], "Voltaic Cave"],
        "generic68-b": [enigmatic[0], enigmatic[1], "Voltaic Cave"],
        "antlerion": [unfathomable[0], unfathomable[1], "Voltaic Cave"],
        "adasparta": [master[0], master[1], "Malware Cave"],
        "magnatoxin": [exquisite[0], exquisite[1], "Malware Cave"],
        "fulmara": [exquisite[0], exquisite[1], "Malware Cave"],
        "archaem": [transcendent[0], transcendent[1], "Malware Cave"],
        "malicioutrite": [transcendent[0], transcendent[1], "Malware Cave"],
        "monojit": [enigmatic[0], enigmatic[1], "Malware Cave"],
        "cataclysmium": [unfathomable[0], unfathomable[1], "Malware Cave"],
        "ghostwalker": [unfathomable[0], unfathomable[1], "Umbragloom Cave"],
        "illumina": [enigmatic[0], enigmatic[1], "Umbragloom Cave"],
        "darkhelm": [transcendent[0], transcendent[1], "Umbragloom Cave"],
        "arachnophyte": [exquisite[0], exquisite[1], "Umbragloom Cave"],
        "solemn lamentine": [exquisite[0], exquisite[1], "Umbragloom Cave"],
        "duskgravite": [mythic[0], mythic[1], "Umbragloom Cave"],
        "weesp": [surreal[0], surreal[1], "Umbragloom Cave"],
        "duatwist": [master[0], master[1], "Umbragloom Cave"],
        "malsite": [rare[0], rare[1], "Umbragloom Cave"],
        "increpus": [uncommon[0], uncommon[1], "Umbragloom Cave"],
        "spooky chocolatine": [uncommon[0], uncommon[1], "Umbragloom Cave"],
        "stygius": [uncommon[0], uncommon[1], "Umbragloom Cave"],
        "blite": [common[0], common[1], "Umbragloom Cave"],
        "soulsalt": [common[0], common[1], "Umbragloom Cave"],
        "pale sand": [common[0], common[1], "Umbragloom Cave"],
        "eggforite": [enigmatic[0], enigmatic[1], "Anti Cave"],
        "copy crystal": [enigmatic[0], enigmatic[1], "Anti Cave"],
        "latsyrc": [enigmatic[0], enigmatic[1], "Anti Cave"],
        "negated crystal": [enigmatic[0], enigmatic[1], "Anti Cave"],
        "thumb crystal": [unfathomable[0], unfathomable[1], "Anti Cave"],
        "malix": [otherworldly[0], otherworldly[1], "Anti Cave"],
        "pinkium": [uncommon[0], uncommon[1], "Marble Cave"],
        "piranite": [rare[0], rare[1], "Marble Cave"],
        "cretium": [rare[0], rare[1], "Marble Cave"],
        "pink-gold pearl": [rare[0], rare[1], "Marble Cave"],
        "kryptonite": [rare[0], rare[1], "Marble Cave"],
        "protonite": [surreal[0], surreal[1], "Marble Cave"],
        "agspernite": [surreal[0], surreal[1], "Marble Cave"],
        "taaffeite": [surreal[0], surreal[1], "Marble Cave"],
        "ethereal gem": [mythic[0], mythic[1], "Marble Cave"],
        "daybreak": [enigmatic[0], enigmatic[1], "Marble Cave"],
        "ultra sinistral": [otherworldly[0], otherworldly[1], "Marble Cave"],
        "shadow bauxite": [uncommon[0], uncommon[1], "Darkmatter Cave"],
        "chroma": [uncommon[0], uncommon[1], "Darkmatter Cave"],
        "heliotrope": [rare[0], rare[1], "Darkmatter Cave"],
        "dark agsperite": [rare[0], rare[1], "Darkmatter Cave"],
        "corrupt opal": [rare[0], rare[1], "Darkmatter Cave"],
        "dark pulsar": [rare[0], rare[1], "Darkmatter Cave"],
        "soul matter": [master[0], master[1], "Darkmatter Cave"],
        "shadow neutronite": [surreal[0], surreal[1], "Darkmatter Cave"],
        "adamantium": [surreal[0], surreal[1], "Darkmatter Cave"],
        "luminous gem": [mythic[0], mythic[1], "Darkmatter Cave"],
        "shadow crystal": [exotic[0], exotic[1], "Darkmatter Cave"],
        "shadow cherkasyl": [unfathomable[0], unfathomable[1], "Darkmatter Cave"],
        "shadow-x": [otherworldly[0], otherworldly[1], "Darkmatter Cave"],
        "lava rock": [common[0], common[1], "Solar Cave"],
        "pumice": [common[0], common[1], "Solar Cave"],
        "tuff": [common[0], common[1], "Solar Cave"],
        "tephra": [common[0], common[1], "Solar Cave"],
        "malachite": [uncommon[0], uncommon[1], "Solar Cave"],
        "bauxite": [uncommon[0], uncommon[1], "Solar Cave"],
        "gabbro": [uncommon[0], uncommon[1], "Solar Cave"],
        "rhyolite": [rare[0], rare[1], "Solar Cave"],
        "fire pearl": [rare[0], rare[1], "Solar Cave"],
        "agsperite": [rare[0], rare[1], "Solar Cave"],
        "black flame": [master[0], master[1], "Solar Cave"],
        "volcanium": [master[0], master[1], "Solar Cave"],
        "fire neutronite": [surreal[0], surreal[1], "Solar Cave"],
        "magma gem": [mythic[0], mythic[1], "Solar Cave"],
        "fire gem": [mythic[0], mythic[1], "Solar Cave"],
        "blaze crystal": [exquisite[0], exquisite[1], "Solar Cave"],
        "cygni": [enigmatic[0], enigmatic[1], "Solar Cave"],
        "x-flare": [unfathomable[0], unfathomable[1], "Solar Cave"],
        "shortcake": [enigmatic[0], enigmatic[1], "Candied Cave"],
        "egerarilia": [enigmatic[0], enigmatic[1], "Eggshell Cave"],
        "jubilyte": [enigmatic[0], enigmatic[1], "Firework Cave"],
        "resonance": [enigmatic[0], enigmatic[1], "Floral Cave"],
        "everbloom": [exotic[0], exotic[1], "Floral Cave"],
        "eleggtricity": [exquisite[0], exquisite[1], "Eggshell Cave"],
        "trifolium": [exquisite[0], exquisite[1], "Lucky Cave"],
        "cl0ver": [transcendent[0], transcendent[1], "Lucky Cave"],
        "pot of rex pesos": [transcendent[0], transcendent[1], "Lucky Cave"],
        "faberge of mining": [transcendent[0], transcendent[1], "Eggshell Cave"],
        "aurovelle": [transcendent[0], transcendent[1], "Firework Cave"],
        "prosperity": [unfathomable[0], unfathomable[1], "Lucky Cave"],
        "retroscade": [unfathomable[0], unfathomable[1], "Firework Cave"],
        "evanessence": [otherworldly[0], otherworldly[1], "Floral Cave"],
        "shellker": [common[0], common[1], "Eggshell Cave"],
        "albumin": [common[0], common[1], "Eggshell Cave"],
        "vogel": [uncommon[0], uncommon[1], "Eggshell Cave"],
        "bonnite": [rare[0], rare[1], "Eggshell Cave"],
        "chalaza": [rare[0], rare[1], "Eggshell Cave"],
        "egguinox": [master[0], master[1], "Eggshell Cave"],
        "bungy": [surreal[0], surreal[1], "Eggshell Cave"],
        "yolkbang": [surreal[0], surreal[1], "Eggshell Cave"],
        "sugarmuck": [master[0], master[1], "Candied Cave"],
        "charmoss": [common[0], common[1], "Lucky Cave"],
        "talismine": [common[0], common[1], "Lucky Cave"],
        "imperial jade": [uncommon[0], uncommon[1], "Lucky Cave"],
        "pixy emerald": [rare[0], rare[1], "Lucky Cave"],
        "gildice": [master[0], master[1], "Lucky Cave"],
        "halcylite": [surreal[0], surreal[1], "Lucky Cave"],
        "rotatrim": [mythic[0], mythic[1], "Lucky Cave"],
        "verdite": [common[0], common[1], "Floral Cave"],
        "blosmite": [common[0], common[1], "Floral Cave"],
        "paxonite": [uncommon[0], uncommon[1], "Floral Cave"],
        "honeycomb": [uncommon[0], uncommon[1], "Floral Cave"],
        "maripollum": [rare[0], rare[1], "Floral Cave"],
        "floresite": [master[0], master[1], "Floral Cave"],
        "beehive": [mythic[0], mythic[1], "Floral Cave"],
    }

    attributes: list[int | str] | None = cave_exclusives.get(ore_name, None)
    if attributes is None:
        return None

    ret_attribs: OreAttributes = OreAttributes()
    ret_attribs.ion_mult = attributes[0]
    ret_attribs.tier_name = attributes[1]
    ret_attribs.cave_type = attributes[2]
    ret_attribs.is_cave_exclusive = ore_name != "aurora polaris" # If we got to this point it's a cave exclusive ore.
    return ret_attribs

def get_ore_rarity(
    ore_name: str, base_rarity: int, ore_type: str,
    cave_type: str | None, loadout: str | None, do_adjusted: bool,
    run_nebulova: bool
) -> int:
    """
    Returns an ore's fixed rarity based on the parameters passed in.

    If run_nebulova = True, fix the ore rarity for nebulova event for ores that spawn 'out-of-cave' through it. The REx tracker does not account for this, so multiply rarities by 3.
    """
    if do_adjusted:
        if cave_type is None:
            return base_rarity

        if run_nebulova and ore_name in CAVE_ORES["Starry Cave"]["ores"]:
            cave_attributes = get_ore_attributes(ore_name=ore_name)
            if cave_attributes is not None:
                is_cave_exclusive = cave_attributes.is_cave_exclusive

                if cave_type == "Gilded Cave" and is_cave_exclusive:
                    base_rarity = CAVE_ORES["Starry Cave"]["ores"][ore_name][ORE_TYPE_TO_RANK.get(ore_type)] * 3
                elif cave_type != "Starry Cave" and cave_type != "Gilded Cave":
                    base_rarity = CAVE_ORES["Starry Cave"]["ores"][ore_name][ORE_TYPE_TO_RANK.get(ore_type)] * 3

        if loadout is not None:  # prevent IndexError in split
            salad_57 = True if ("Ambrosia Salad" in loadout or loadout.split(", ")[0] == "57 Leaf Clover") else False
            salad_100 = True if (loadout.split(", ")[0] == "100 Leaf Clover") else False
        else:
            salad_57 = False
            salad_100 = False

        adjusted: int = base_rarity * (
            CAVE_ORES[cave_type]['rarity'] if cave_type != "Gilded Cave" else 57 if salad_57 else 100 if salad_100 else 5700)

        is_floor_exclusive: bool = ore_name == "Empress of Light" or ore_name == "Aurora Polaris" or ore_name == "Solemn Lamentine" or ore_name == "Bungy"
        if is_floor_exclusive:
            adjusted *= 3.5846

        return round(adjusted)
    else:
        if base_rarity == 0:
            ores = {
                'Zanarchium': 68750000 * (10 if ore_type == "IONIZED" else 150 if ore_type == "SPECTRAL" else 1),
                'Protoflare': 2000000 * (45 if ore_type == "IONIZED" else 675 if ore_type == "SPECTRAL" else 1)  # event roll rarity
            }
            return ores.get(ore_name, 0)

        if run_nebulova is not None and cave_type is not None and ore_name in CAVE_ORES["Starry Cave"][
            "ores"] and cave_type != "Starry Cave" and cave_type != "Gilded Cave":
            base_rarity = CAVE_ORES["Starry Cave"]["ores"][ore_name][ORE_TYPE_TO_RANK.get(ore_type)] * 3

        return base_rarity

def is_owner(user_id: int) -> bool:
    """
    Returns if the user is the owner of this bot.
    Used for commands so you can override permissions and run anything.
    """
    return config.DEV_MODE or user_id == 475737475470589952

def get_permission_level(user_id: int) -> PermissionLevel:
    """
    Returns permission level for command usage. 
    Owner means they can run anything,
    Admin means they can run certain things others can't (manual track for example),
    Default means no special permissions.
    """

    if is_owner(user_id=user_id):
        return PermissionLevel.OWNER # No need to do anything else

    permission_level: PermissionLevel = PermissionLevel.DEFAULT

    bot_guild: discord.Guild | None = bot.get_guild(1177151218049618031)
    if bot_guild is None:
        return permission_level
    
    member: discord.Member | None = bot_guild.get_member(user_id)
    if member is None:
        return permission_level
    
    whitelist_role: discord.Role | None = discord.utils.get(iterable=bot_guild.roles, id=1195956111099052032)
    whitelist_plus_role: discord.Role | None = discord.utils.get(iterable=bot_guild.roles, id=1328207797321601046)
    if whitelist_role is not None and whitelist_plus_role is not None:
        if whitelist_plus_role in member.roles:
            permission_level = PermissionLevel.OWNER
        elif whitelist_role in member.roles:
            permission_level = PermissionLevel.ADMIN
    
    return permission_level

def get_nth_word(string: str, n: int, delim: str | None = None) -> str | None:
    """
    Return the word at the nth position of the string.
    Returns None if there is not n words in the string.
    """
    words: list[str] = string.split(sep=delim)
    if 1 <= n <= len(words):
        return words[n-1]
    return None

def find_closest_names(ore_name: str) -> list[str] | str | None:
    ore_name = ore_name.lower()
    symbol_ores_list: tuple[str] = ('sigma', 'pi', 'omega', 'lunar omega', 'delta', 'psi', 'infinictrite', 'noopa', 'noo p a')
    number_ores_list: tuple[str] = ('combustion system', 'trojan')
    if ore_name in symbol_ores_list:
        return ('Σ', 'π', 'Ω', 'Lunar Ω', 'Δ', 'ψ', '∞', 'NOO P α', 'NOO P α')[symbol_ores_list.index(ore_name)]
    elif ore_name in number_ores_list:
        return ('@Combust10n_+_Syst3m', 'TR0J4N')[number_ores_list.index(ore_name)]

    name_list: dict[str, int] | None = ALL_ORES.get('Ores', None)
    if name_list is None:
        raise RuntimeError
    
    name_list_lower: dict[str, str] = { name.lower(): name for name in name_list }
    matches = difflib.get_close_matches(ore_name, name_list_lower.keys(), 25)

    if len(matches) == 0:
        return None

    return [name_list_lower[match] for match in matches]

def ore_name_autocomplete(ctx: discord.AutocompleteContext) -> list[str]:
    if not ctx.value: return ["Enter an ore name!"]
    ore_names = find_closest_names(ctx.value.lower())
    if not ore_names or len(ore_names) == 0: return ["Enter a valid ore name!"]
    vals = [c for c in ore_names if ctx.value.lower() in c.lower()][:5]
    return vals

def cave_type_autocomplete(ctx: discord.AutocompleteContext) -> list[str]:
    if not ctx.value: return ["Enter a cave type!"]
    return [c for c in CAVE_ORES.keys() if ctx.value.lower() in c.lower()][:5]

def get_global_role_ping(ore_name: str, ore_rarity: int, ore_rank: OreTiers, ore_type: str, cave_type: str) -> str:
    # This sucks! but oh well.
    event_rarities: dict[str, int] = {
        "idolium": 140_000_000,
        "inclemetite": 225_000_000,
        "illusory bubblegram": 342_000_040,
        "acrimony": 191_847_000,
        "noo p α": 565_656_000,
        "ephemryst": 190_520_000,
        "vocarus": 200_500_500,
        "hallownest": 210_167_002,
        "reminiscence": 234_030_360,
        "yuki onna": 350_100_200,
        "wintburg": 590_200_035,
        "antlerion": 11_086_357,
        "mekanos": 320_830_300,
        "theon": 590_300_300,
        "c◊smic_split": 840_500_000,
        "x-flare": 31_250_000,
        "troylezian": 222_333_444,
        "serotonin": 432_198_765,
        "prisma": 1_222_222_222,
        "shadow-x": 136_932_133,
        "∞": 20_000_000_000
    }

    base_ore_rarity: int = get_ore_rarity(ore_name=ore_name, base_rarity=ore_rarity, ore_type=ore_type, cave_type=cave_type, loadout=None, do_adjusted=False, run_nebulova=False)
    adjusted_ore_rarity: int = get_ore_rarity(ore_name=ore_name, base_rarity=ore_rarity, ore_type=ore_type, cave_type=cave_type, loadout=None, do_adjusted=True, run_nebulova=True)
    adjusted_ore_rarity = round(adjusted_ore_rarity * 1.88)

    event_ore_rarity: int = event_rarities.get(ore_name, base_ore_rarity)
    if ore_type != "NORMAL":
        if ore_rank == OreTiers.UNFATHOMABLE:
            event_ore_rarity *= 20
        else:
            event_ore_rarity *= 15
        if ore_type == "SPECTRAL":
            event_ore_rarity *= 15

    attributes: OreAttributes | None = get_ore_attributes(ore_name=ore_name)
    cave_exclusive: bool = attributes is not None and attributes.is_cave_exclusive
    
    normal_cave_exc_unfaths: tuple[str] = ("cataclysmium", "antlerion", "thermazine", "low.hp", "empress of light", "thumb crystal", "x-flare", "shadow cherkasyl", "ghostwalker", "retroscade", "prosperity")
    ion_cave_exc_enigs: tuple[str] = ("monojit", "illusorium", "collapse", "sword waltz", "geometrix", "generic68-b", "astraea", "aetherion", "shortcake", "resonance", "egerarilia", "jubilyte")
    if (ore_rank == OreTiers.UNFATHOMABLE and ore_type == "NORMAL" and not cave_type) or\
        (ore_rank == OreTiers.ENIGMATIC and ore_type == "IONIZED" and not cave_exclusive and not cave_type) or\
        (ore_name in normal_cave_exc_unfaths and ore_type == "NORMAL") or\
        (ore_name in ion_cave_exc_enigs and ore_type == "IONIZED") or\
        (ore_rank == OreTiers.ZENITH and ore_type == "NORMAL") or\
        (ore_rank == OreTiers.EXCLUSIVE):
        return "<@&1371968654328991895>\n"
    elif (ore_rank == OreTiers.OTHERWORLDLY and event_ore_rarity <= 1_500_000_000 and not cave_type and ore_type == "NORMAL") or\
        (ore_rank == OreTiers.UNFATHOMABLE and cave_exclusive and (ore_type == "NORMAL" or ore_type == "IONIZED")) or\
        (ore_rank == OreTiers.UNFATHOMABLE and adjusted_ore_rarity <= 7_000_000_000 and cave_type and ore_type == "NORMAL") or\
        (ore_rank == OreTiers.ENIGMATIC and cave_exclusive and ore_name != "hyperheated quasar" and ore_type == "IONIZED") or\
        (ore_rank == OreTiers.TRANSCENDENT and ore_type == "SPECTRAL" and not cave_type) or\
        (ore_rank == OreTiers.UNFATHOMABLE and ore_type == "IONIZED" and event_ore_rarity <= (300000000 * 20) and not cave_type) or\
        ((ore_name == "machina" or ore_name == "syderea") and ore_type == "NORMAL"):
        return "## <@&1473111240116273214>\n<@&1371968654328991895>\n"
    else:
        return "# ***<@&1473111272538243082>***\n**<@&1473111240116273214>** <@&1371968654328991895>\n"
    