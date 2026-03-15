from dataclasses import dataclass

from Options import Choice, PerGameCommonOptions, Range, Toggle, OptionGroup


class GamePace(Choice):
    """
    Determines the speed at which the world will be played.

    Quick: Start with 20 minutes, gain 20 with each time bonus.
    4 or 5 time bonuses will generate, and you will have a few large spheres.
    A full playthrough can take around ?? hours.

    Standard: Start with 10 minutes, gain 10 with each time bonus.
    7 to 9 time bonuses will generate, and you will have a moderate number of moderate spheres.
    A full playthrough can take around ?? hours.

    Glacial: Start with 5 minutes, gain 5 with each time bonus.
    15 to 19 time bonuses will generate, and you will have a lot of small spheres.
    A full playthrough can take around ?? hours.
    """

    display_name = "Progression Pacing"

    option_quick = 0
    option_standard = 1
    option_glacial = 2

    default = option_standard

class ScoreLocations(Range):
    """
    How many locations are locked behind score requirements.
    """

    display_name = "Score Checks"

    range_start = 50
    range_end = 200
    default = 100

class BotCount(Toggle):
    """
    Whether BigLobby is installed.
    If true then more than 3 bots are allowed to generate,
    however the game may become less stable:
    https://modworkshop.net/mod/21582
    """

    display_name = "BigLobby"

class AdditionalSaw(Range):
    """
    How many OVE9000 saws are in the item pool.
    Your first saw will randomly be a primary or secondary.
    """

    display_name = "Saws"

    range_start = 0
    range_end = 2

    default = 2

class NineLives(Range):
    """
    How many Nine Lives upgrades are available.
    Nine Lives Lv1: 2 total downs.
    Nine Lives Lv2: 4 total downs.
    """

    display_name = "Nine Lives"

    range_start = 0
    range_end = 2

    default = 2

class PrimaryCount(Range):
    """
    How many primary weapons are guaranteed to generate in the multiworld.
    18 is the most you can have without DLC - extra items will do nothing.
    """

    display_name = "Primary Weapons"

    range_start = 0
    range_end = 72
    default = 10

class AkimboCount(Range):
    """
    How many akimbos are guaranteed to generate in the multiworld.
    44 is the most you can have without DLC - extra items will do nothing.
    """

    display_name = "Akimbos"

    range_start = 0
    range_end = 57
    default = 5

class SecondaryCount(Range):
    """
    How many secondary weapons are guaranteed to generate in the multiworld.
    23 is the most you can have without DLC - extra items will do nothing.
    """

    display_name = "Secondary Weapons"

    range_start = 0
    range_end = 66
    default = 10

class MeleeCount(Range):
    """
    How many melee weapons are guaranteed to generate in the multiworld.
    18 is the most you can have without DLC - extra items will do nothing.
    """

    display_name = "Melee Weapons"

    range_start = 0
    range_end = 86
    default = 5

class ThrowableCount(Range):
    """
    How many throwables are guaranteed to generate in the multiworld.
    5 is the most you can have without DLC - extra items will do nothing.
    """

    display_name = "Throwables"

    range_start = 0
    range_end = 9
    default = 5

class MaxDiff(Choice):
    """
    The highest difficulty your run can reach.
    """

    display_name = "Final Difficulty"

    option_overkill = 4
    option_mayhem = 5
    option_death_wish = 6
    option_death_sentence = 7

    default = 6

class DeathLink(Toggle):
    """
    Death links are sent every time a heist is failed.
    After receiving a death link you will lose a down the next time you take damage.
    In a multiplayer session only the lobby host can send death links to avoid spam.
    """

    display_name = "Death Link"


@dataclass
class PAYDAY2Options(PerGameCommonOptions):
    progression_pacing: GamePace
    score_checks: ScoreLocations
    biglobby: BotCount
    saws: AdditionalSaw
    primary_weapons: PrimaryCount
    akimbo: AkimboCount
    secondary_weapons: SecondaryCount
    melee_weapons: MeleeCount
    throwables: ThrowableCount
    final_difficulty: MaxDiff
    death_link: DeathLink

option_groups = [
    OptionGroup(
        "Item Generation",
        [BotCount, AdditionalSaw, PrimaryCount, AkimboCount,
         SecondaryCount, MeleeCount, ThrowableCount],
    ),
]