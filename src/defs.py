import discord, enum, json, logging, sqlite3
from discord.ext import commands
from typing import Any, TypeAlias

intents = discord.Intents.default()
intents.message_content = True
bot: discord.Bot = discord.Bot(intents=intents)

REX_WEBHOOK_UIDS: tuple[int, int, int] = (
    1259168578419163166, 1259168752591966229, 1259168868581113947
)  # stax; rex webhook user ids, normal - spectral
REX_TRACKER_CHANNEL_IDS: tuple[int, int, int] = (
    967252613227769876, 967252672170299402, 967252684807749752
)  # stax; rex tracker channel ids, normal - spectral

DiscordChannel: TypeAlias = discord.TextChannel | discord.VoiceChannel | discord.StageChannel | discord.Thread | discord.DMChannel | discord.GroupChannel | None

class MissingPermissions(commands.CommandError):
    """
    Raised when a user runs a command and fails to have the correct permissions to run it.
    """

    # Copied from the base class, edited slightly
    def __init__(self, message: str | None = None, *args: Any) -> None:
        if message is not None:
            new_message: str = discord.utils.escape_mentions(text=message)
            super().__init__(new_message, *args)
        else:
            super().__init__(*args)

db_conn: sqlite3.Connection = sqlite3.connect("database.db")
db_cursor: sqlite3.Cursor = db_conn.cursor()

# stax; don't remove the src/ prefix because cybrancee will shit itself
with open("src/cave_ores.json", "r", encoding="utf-8") as cave_ores_json:
    CAVE_ORES: dict[str, dict[str, int | dict[str, list[int]]]] = json.load(cave_ores_json)
with open("src/all_ores.json", "r", encoding="utf-8") as all_ores_json:
    ALL_ORES: dict[str, dict[str, int]] = json.load(all_ores_json)

logger: logging.Logger = logging.getLogger(name="logger")
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

class TierNames(enum.StrEnum):
    COMMON = "Common",
    UNCOMMON = "Uncommon"
    RARE = "Rare"
    MASTER = "Master"
    SURREAL = "Surreal"
    MYTHIC = "Mythic"
    EXOTIC = "Exotic"
    EXQUISITE = "Exquisite"
    TRANSCENDENT = "Transcendent"
    ENIGMATIC = "Enigmatic"
    UNFATHOMABLE = "Unfathomable"
    OTHERWORLDLY = "Otherworldly"
    IMAGINARY = "Imaginary"
    ZENITH = "Zenith"
    EXCLUSIVE = "Exclusive"

TIER_COLOR_TO_TIER_NAME = {  # stax; NEVER TOUCH THESE, WILL BREAK TRACKERS!
    "#c1c1c1": TierNames.COMMON,
    "#ff2626": TierNames.UNCOMMON,
    "#ff8001": TierNames.RARE,
    "#9900e5": TierNames.MASTER,
    "#1cd6a8": TierNames.SURREAL,
    "#ff00ea": TierNames.MYTHIC,
    "#f5c83f": TierNames.EXOTIC,
    "#55c264": TierNames.EXQUISITE,
    "#007fff": TierNames.TRANSCENDENT,
    "#ccf500": TierNames.ENIGMATIC,
    "#022b78": TierNames.UNFATHOMABLE,
    "#5d0d31": TierNames.OTHERWORLDLY,
    "#ffe89e": TierNames.IMAGINARY,
    "None": TierNames.ZENITH,
    "#26004b": TierNames.EXCLUSIVE
}

TIER_NAME_TO_TIER_RANK = {
    TierNames.COMMON: OreTiers.COMMON,
    TierNames.UNCOMMON: OreTiers.UNCOMMON,
    TierNames.RARE: OreTiers.RARE,
    TierNames.MASTER: OreTiers.MASTER,
    TierNames.SURREAL: OreTiers.SURREAL,
    TierNames.MYTHIC: OreTiers.MYTHIC,
    TierNames.EXOTIC: OreTiers.EXOTIC,
    TierNames.EXQUISITE: OreTiers.EXQUISITE,
    TierNames.TRANSCENDENT: OreTiers.TRANSCENDENT,
    TierNames.ENIGMATIC: OreTiers.ENIGMATIC,
    TierNames.UNFATHOMABLE: OreTiers.UNFATHOMABLE,
    TierNames.OTHERWORLDLY: OreTiers.OTHERWORLDLY,
    TierNames.IMAGINARY: OreTiers.IMAGINARY,
    TierNames.ZENITH: OreTiers.ZENITH,
    TierNames.EXCLUSIVE: OreTiers.EXCLUSIVE
}

TIER_NAME_TO_COLOR_HEX = {
    TierNames.COMMON: 0xC1C1C1,
    TierNames.UNCOMMON: 0xFF2626,
    TierNames.RARE: 0xFF8001,
    TierNames.MASTER: 0x9900E5,
    TierNames.SURREAL: 0x1CD6A8,
    TierNames.MYTHIC: 0xFF00EA,
    TierNames.EXOTIC: 0xF6C940,
    TierNames.EXQUISITE: 0x55C264,
    TierNames.TRANSCENDENT: 0x007FFF,
    TierNames.ENIGMATIC: 0xCCF500,
    TierNames.UNFATHOMABLE: 0x022B78,
    TierNames.OTHERWORLDLY: 0x5D0D31,
    TierNames.IMAGINARY: 0XFFE89E,
    TierNames.ZENITH: 0x010101,
    TierNames.EXCLUSIVE: 0x26004B
}

class PermissionLevel(enum.IntEnum):
    DEFAULT = 1,
    ADMIN = 2,
    OWNER = 3

class AdjustedPreferences(enum.IntEnum):
    NONE = 0,
    BASE = 1,
    CONSTANT = 2,
    BOTH = 3,

