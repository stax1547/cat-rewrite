import discord
import enum
import json
import logging
import sqlite3

intents = discord.Intents.default()
intents.message_content = True
bot: discord.Bot = discord.Bot(intents=intents)

REX_WEBHOOK_UIDS = [
    1259168578419163166, 1259168752591966229, 1259168868581113947
]  # stax; rex webhook user ids, normal - spectral
REX_TRACKER_CHANNEL_IDS = [
    967252613227769876, 967252672170299402, 967252684807749752
]  # stax; rex tracker channel ids, normal - spectral

db_conn = sqlite3.connect("database.db")
db_cursor = db_conn.cursor()

# stax; don't remove the src/ prefix because cybrancee will shit itself
with open("src/cave_ores.json", "r", encoding="utf-8") as cave_ores_json:
    CAVE_ORES: dict = json.load(cave_ores_json)

logger = logging.getLogger(name="logger")
logging.basicConfig(
    filename="log.log",
    filemode="a",
    level=logging.INFO,
    format="%(asctime)s;%(levelname)s;%(message)s",
)

TYPE_BY_CHANNEL_IDS = {
    967252613227769876: "NORMAL",
    967252672170299402: "IONIZED",
    967252684807749752: "SPECTRAL",
}


class OreTypes(enum.IntEnum):
    NORMAL = 0,
    IONIZED = 1,
    SPECTRAL = 2


ORE_TYPE_TO_RANK = {
    "NORMAL": OreTypes.NORMAL,
    "IONIZED": OreTypes.IONIZED,
    "SPECTRAL": OreTypes.SPECTRAL
}


class OreTiers(enum.IntEnum):
    COMMON = 1,
    UNCOMMON = 2,
    RARE = 3,
    MASTER = 4,
    SURREAL = 5,
    MYTHIC = 6,
    EXOTIC = 7,
    EXQUISITE = 8,
    TRANSCENDENT = 9,
    ENIGMATIC = 10,
    UNFATHOMABLE = 11,
    OTHERWORLDLY = 12,
    IMAGINARY = 13,
    ZENITH = 14,
    EXCLUSIVE = 15


TIER_COLOR_TO_TIER_NAME = {  # stax; NEVER TOUCH THESE, WILL BREAK TRACKERS!
    "#c1c1c1": "Common",
    "#ff2626": "Uncommon",
    "#ff8001": "Rare",
    "#9900e5": "Master",
    "#1cd6a8": "Surreal",
    "#ff00ea": "Mythic",
    "#f5c83f": "Exotic",
    "#55c264": "Exquisite",
    "#007fff": "Transcendent",
    "#ccf500": "Enigmatic",
    "#022b78": "Unfathomable",
    "#5d0d31": "Otherworldly",
    "#ffe89e": "Imaginary",
    "None": "Zenith",
    "#26004b": "Exclusive"
}

TIER_NAME_TO_TIER_RANK = {
    "Common": OreTiers.COMMON,
    "Uncommon": OreTiers.UNCOMMON,
    "Rare": OreTiers.RARE,
    "Master": OreTiers.MASTER,
    "Surreal": OreTiers.SURREAL,
    "Mythic": OreTiers.MYTHIC,
    "Exotic": OreTiers.EXOTIC,
    "Exquisite": OreTiers.EXQUISITE,
    "Transcendent": OreTiers.TRANSCENDENT,
    "Enigmatic": OreTiers.ENIGMATIC,
    "Unfathomable": OreTiers.UNFATHOMABLE,
    "Otherworldly": OreTiers.OTHERWORLDLY,
    "Imaginary": OreTiers.IMAGINARY,
    "Zenith": OreTiers.ZENITH,
    "Exclusive": OreTiers.EXCLUSIVE
}

TIER_NAME_TO_COLOR_HEX = {
    "Common": 0xC1C1C1,
    "Uncommon": 0xFF2626,
    "Rare": 0xFF8001,
    "Master": 0x9900E5,
    "Surreal": 0x1CD6A8,
    "Mythic": 0xFF00EA,
    "Exotic": 0xF6C940,
    "Exquisite": 0x55C264,
    "Transcendent": 0x007FFF,
    "Enigmatic": 0xCCF500,
    "Unfathomable": 0x022B78,
    "Otherworldly": 0x5D0D31,
    "Imaginary": 0XFFE89E,
    "Zenith": 0x010101,
    "Exclusive": 0x26004B
}

# stax; cave type rarities.
CAVE_RARITIES = {
    "Gilded Cave": 5700,
    "Frozen Cave": 8,
    "Metallic Cave": 11,
    "Geode Cave": 12,
    "Elemental Cave": 17,
    "Divine Cave": 20,
    "Prismatic Cave": 27,
    "Void Cave": 35,
    "Magmatic Cave": 11,
    "Radioactive Cave": 11,
    "Interstellar Cave": 11,
    "nil Cave": 48,
    "feebium Cave": 99999,
    "Unstable Cave": 13,
    "Galactic Cave": 16,
    "Enchanted Cave": 22,
    "Luminous Cave": 34,
    "Nightfall Cave": 43,
    "Solar Cave": 7,
    "Darkmatter": 15,
    "Marble Cave": 25,
    "Anti-Cave Cave": 96,
    "Starry Cave": 9,
    "Matrix Cave": 15,
    "Voltaic Cave": 17,
    "Bichromatic Cave": 21,
    "Monoprismatic Cave": 29,
    "Malware Cave": 36,
    "Soulseek Cave": 11,
    "Heartstring Cave": 14,
    "Snowveil Cave": 20,
    "Freezeflower Cave": 22,
    "Fractured Cave": 35,
    "Umbragloom Cave": 8,
    "Softsnow Cave": 12,
    "Firework Cave": 20,
    "Peppermint Cave": 25,
    "Fireplace Cave": 33,
}

class AdjustedPreferences(enum.IntEnum):
    NONE = 0,
    BASE = 1,
    CONSTANT = 2,
    BOTH = 3,

