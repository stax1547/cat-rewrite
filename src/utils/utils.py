import decimal

from utils.defs import *


class OreAttributes:
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
    common = [110, "Common"]
    uncommon = [100, "Uncommon"]
    rare = [90, "Rare"]
    master = [80, "Master"]
    surreal = [70, "Surreal"]
    mythic = [60, "Mythic"]
    exotic = [50, "Exotic"]
    exquisite = [45, "Exquisite"]
    transcendent = [40, "Transcendent"]
    enigmatic = [30, "Enigmatic"]
    unfathomable = [20, "Unfathomable"]
    otherworldly = [15, "Otherworldly"]

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
        "amalton": [transcendent[0], transcendent[1], "Soulseek Cave"],
        "heretic's cage": [enigmatic[0], enigmatic[1], "Soulseek Cave"],
        "lovestruck": [exquisite[0], exquisite[1], "Heartstring Cave"],
        "amorisene": [enigmatic[0], enigmatic[1], "Heartstring Cave"],
        "cursed flesh": [transcendent[0], transcendent[1], "Fractured Cave"],
        "vigilance": [transcendent[0], transcendent[1], "Fractured Cave"],
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
        "eggforite": [enigmatic[0], enigmatic[1], "Anti-Cave Cave"],
        "copy crystal": [enigmatic[0], enigmatic[1], "Anti-Cave Cave"],
        "latsyrc": [enigmatic[0], enigmatic[1], "Anti-Cave Cave"],
        "negated crystal": [enigmatic[0], enigmatic[1], "Anti-Cave Cave"],
        "thumb crystal": [unfathomable[0], unfathomable[1], "Anti-Cave Cave"],
        "malix": [otherworldly[0], otherworldly[1], "Anti-Cave Cave"],
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
    }

    attributes = cave_exclusives.get(ore_name, None)
    if not attributes:
        return None

    ret_attribs: OreAttributes = OreAttributes()
    ret_attribs.cave_type = attributes[2]
    ret_attribs.is_cave_exclusive = ore_name != "aurora polaris"
    return ret_attribs


def get_ore_rarity(
    ore_name: str, base_rarity: int, ore_type: str,
    cave_type: str, loadout: str, do_adjusted: bool,
    run_nebulova: bool
) -> int:
    """
    Returns an ore's fixed rarity based on the parameters passed in.

    If run_nebulova = True, fix the ore rarity for nebulova event for ores that spawn 'out-of-cave' through it. The REx tracker does not account for this, so we have to multiply rarities by 3.
    """
    if do_adjusted:
        if not cave_type:
            return base_rarity

        if run_nebulova and ore_name in CAVE_ORES["Starry Cave"]["ores"]:
            cave_attributes = get_ore_attributes(ore_name=ore_name)
            is_cave_exclusive = cave_attributes.is_cave_exclusive

            if cave_type == "Gilded Cave" and is_cave_exclusive:
                base_rarity = CAVE_ORES["Starry Cave"]["ores"][ore_name][ORE_TYPE_TO_RANK.get(ore_type)] * 3
            elif cave_type != "Starry Cave" and cave_type != "Gilded Cave":
                base_rarity = CAVE_ORES["Starry Cave"]["ores"][ore_name][ORE_TYPE_TO_RANK.get(ore_type)] * 3

        if loadout and loadout != "":  # prevent IndexError in split
            salad = True if ("Ambrosia Salad" in loadout or loadout.split(", ")[0] == "57 Leaf Clover") else False
        else:
            salad = False

        adjusted = base_rarity * (
            CAVE_ORES[str(cave_type)]['rarity'] if cave_type != "Gilded Cave" else 57 if salad else 5700)

        is_floor_exclusive = ore_name == "Empress of Light" or ore_name == "Aurora Polaris" or ore_name == "Solemn Lamentine"
        if is_floor_exclusive:
            adjusted *= decimal.Decimal(3.5846)

        return round(adjusted)
    else:
        if base_rarity == 0:
            ores = {
                'Zanarchium': 68750000 * (10 if ore_type == "IONIZED" else 150 if ore_type == "SPECTRAL" else 1),
                'Protoflare': 2000000 * (45 if ore_type == "IONIZED" else 675 if ore_type == "SPECTRAL" else 1)
                # event roll rarity
            }
            return ores.get(ore_name, 0)

        if run_nebulova is not None and cave_type is not None and ore_name in CAVE_ORES["Starry Cave"][
            "ores"] and cave_type != "Starry Cave" and cave_type != "Gilded Cave":
            base_rarity = CAVE_ORES["Starry Cave"]["ores"][ore_name][ORE_TYPE_TO_RANK.get(ore_type)] * 3

        return base_rarity

def is_owner(user_id: int) -> bool:
    return user_id == 475737475470589952