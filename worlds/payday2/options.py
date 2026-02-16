from dataclasses import dataclass

from Options import Choice, OptionGroup, PerGameCommonOptions, Range, Toggle

class BotCount(Range):
    """
    How many bots will be in the item pool.
    More than 3 requires BigLobby3: https://modworkshop.net/mod/21582
    """

    display_name = "Bot Count"

    range_start = 0
    range_end = 21
    default = "random-range-1-3"

# We must now define a dataclass inheriting from PerGameCommonOptions that we put all our options in.
# This is in the format "option_name_in_snake_case: OptionClassName".
@dataclass
class PAYDAY2Options(PerGameCommonOptions):
    bot_count: BotCount

# If we want to group our options by similar type, we can do so as well. This looks nice on the website.
option_groups = [
    OptionGroup(
        "Gameplay Options",
        [BotCount],
    ),
]