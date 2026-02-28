from dataclasses import dataclass

from Options import Choice, OptionGroup, PerGameCommonOptions, Range, Toggle, OptionSet

class ScoreLocations(Range):
    """
    How many checks are gained from score.
    """

    display_name = "Score Checks"

    range_start = 15
    range_end = 1000
    default = 100

class StartingTime(Range):
    """
    How many minutes you start with before time upgrades.
    """

    display_name = "Starting Time"

    range_start = 1
    range_end = 100
    default = 10

class TimeUpgrades(Range):
    """
    Number of time upgrades to try to add to the item pool.
    If max time is below 60 minutes or above 100 minutes this will be adjusted to fit.
    """

    display_name = "Time Upgrades"

    range_start = 0
    range_end = 99
    default = 5

class TimeUpgradeStrength(Range):
    """
    How many minutes you gain from each time upgrade.
    """

    display_name = "Time Added Per Upgrade"

    range_start = 1
    range_end = 99
    default = 10

class BotCount(Range):
    """
    How many bots will be in the item pool.
    More than 3 requires BigLobby3 and may make the game less stable:
    https://modworkshop.net/mod/21582
    """

    display_name = "Max Bots"

    range_start = 0
    range_end = 21
    default = 3

class AdditionalSaw(Range):
    """
    How many saws are in the item pool.
    """

    display_name = "Saws"

    range_start = 0
    range_end = 2

    default = 1

class PrimaryCount(Range):
    """
    The minimum number of primary weapons in the item pool.
    18 is the most you can have without DLC - extra items will do nothing.
    """

    display_name = "Primary Weapons"

    range_start = 0
    range_end = 72
    default = 10

class AkimboCount(Range):
    """
    The minimum number of akimbos in the item pool.
    44 is the most you can have without DLC - extra items will do nothing.
    """

    display_name = "Akimbos"

    range_start = 0
    range_end = 57
    default = 10

class SecondaryCount(Range):
    """
    The minimum number of secondary weapons in the item pool.
    23 is the most you can have without DLC - extra items will do nothing.
    """

    display_name = "Secondary Weapons"

    range_start = 0
    range_end = 66
    default = 10

class MeleeCount(Range):
    """
    The minimum number of melee weapons in the item pool.
    18 is the most you can have without DLC - extra items will do nothing.
    """

    display_name = "Melee Weapons"

    range_start = 0
    range_end = 86
    default = 5

class ThrowableCount(Range):
    """
    The minimum number of throwables in the item pool.
    5 is the most you can have without DLC - extra items will do nothing.
    """

    display_name = "Throwables"

    range_start = 0
    range_end = 9
    default = 5

class ArmorCount(Range):
    """
    The minimum number of armor unlocks in the item pool.
    """

    display_name = "Armors"

    range_start = 0
    range_end = 6
    default = 6

class DeployablesCount(Range):
    """
    The minimum number of unimportant deployable unlocks in the item pool.
    ECMs and trip mines will always generate somewhere in the multiworld.
    """

    display_name = "Deployables"

    range_start = 0
    range_end = 7
    default = 7

class MinDiff(Choice):
    """
    This is the difficulty your run starts on.
    Higher difficulties give a bigger score multiplier,
    so raising this will speed up the early game.
    """

    display_name = "Starting Difficulty"

    option_normal = 0
    option_hard = 1
    option_very_hard = 2
    option_overkill = 3
    option_mayhem = 4
    option_death_wish = 5
    option_death_sentence = 6

    default = 0

class MaxDiff(Choice):
    """
    This is the highest difficulty your run can reach.
    Higher difficulties give a bigger score multiplier,
    so lowering this will slow the late game.
    """

    display_name = "Final Difficulty"

    option_normal = 1
    option_hard = 2
    option_very_hard = 3
    option_overkill = 4
    option_mayhem = 5
    option_death_wish = 6
    option_death_sentence = 7

    default = 6

class OneDown(Choice):
    """
    Activates the One Down modifier.
    When One Down is active all points earned are doubled.
    """

    display_name = "One Down"

    option_disabled = 0
    option_in_item_pool = 1
    option_enabled = 2

    default = 1

class DiffTraps(Choice):
    """
    Difficulty traps permanently increase the difficulty by 1 per trap collected,
    but also grant a score multiplier.
    Difficulty traps will not bypass your maximum difficulty.
    """

    display_name = "Difficulty Traps"

    option_disabled = 0
    option_enabled = 1
    default = 1

class MutatorTraps(Range):
    """
    How many mutator traps to add to the item pool.
    Mutator traps cause every heist to roll 1 additional mutator,
    but also grant a score multiplier.
    """

    display_name = "Mutator Traps"

    range_start = 0
    range_end = 5
    default = 5

# We must now define a dataclass inheriting from PerGameCommonOptions that we put all our options in.
# This is in the format "option_name_in_snake_case: OptionClassName".
@dataclass
class PAYDAY2Options(PerGameCommonOptions):
    score_checks: ScoreLocations
    starting_time: StartingTime
    time_upgrades: TimeUpgrades
    time_bonus: TimeUpgradeStrength
    bots: BotCount
    armor_unlocks: ArmorCount
    deployables: DeployablesCount
    saws: AdditionalSaw
    primary_weapons: PrimaryCount
    akimbo: AkimboCount
    secondary_weapons: SecondaryCount
    melee_weapons: MeleeCount
    throwables: ThrowableCount
    starting_difficulty: MinDiff
    final_difficulty: MaxDiff
    one_down: OneDown
    difficulty_traps: DiffTraps
    mutator_traps: MutatorTraps