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
    More than 3 requires BigLobby3: https://modworkshop.net/mod/21582
    """

    display_name = "Max Bots"

    range_start = 0
    range_end = 21
    default = 3

class AdditionalSaw(Choice):
    """
    Adds a second saw to the item pool.
    When disabled you can only get one saw (primary or secondary).
    """

    display_name = "Second Saw"

    option_disabled = 0
    option_enabled = 1

    default = 1

class PrimaryCount(Range):
    """
    The max number of primary weapons in the item pool.
    The actual number depends on how many locations you have.
    62 is the most you can have without any DLC - going over will create items that do nothing.
    """

    display_name = "Max Primary Weapons"

    range_start = 0
    range_end = 131
    default = 62

class SecondaryCount(Range):
    """
    The max number of secondary weapons in the item pool.
    The actual number depends on how many locations you have.
    28 is the most you can have without any DLC - going over will create items that do nothing.
    """

    display_name = "Max Secondary Weapons"

    range_start = 0
    range_end = 76
    default = 28

class MeleeCount(Range):
    """
    The max number of melee weapons in the item pool.
    The actual number depends on how many locations you have.
    17 is the most you can have without any DLC - going over will create items that do nothing.
    """

    display_name = "Max Melee Weapons"

    range_start = 0
    range_end = 75
    default = 17

class ThrowableCount(Range):
    """
    The max number of throwables in the item pool.
    The actual number depends on how many locations you have.
    5 is the most you can have without any DLC - going over will create items that do nothing.
    """

    display_name = "Max Throwables"

    range_start = 0
    range_end = 8
    default = 5

class ArmorCount(Range):
    """
    The max number of armor unlocks in the item pool.
    The actual number depends on how many locations you have.
    """

    display_name = "Max Armors"

    range_start = 0
    range_end = 6
    default = 6

class DeployablesCount(Range):
    """
    The max number of non-progression deployable unlocks in the item pool.
    The actual number depends on how many locations you have.
    """

    display_name = "Max Deployables"

    range_start = 0
    range_end = 7
    default = 7

class MinDiff(Choice):
    """
    This is the difficulty your run starts on.
    Higher difficulties give a score multiplier,
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
    Higher difficulties give a score multiplier,
    so lowering this will slow the late game.
    """

    display_name = "Highest Difficulty"

    option_normal = 0
    option_hard = 1
    option_very_hard = 2
    option_overkill = 3
    option_mayhem = 4
    option_death_wish = 5
    option_death_sentence = 6

    default = 5

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
    Whether to add difficulty traps to the item pool or not.
    Difficulty traps permanently increase the difficulty by 1 per trap collected,
    but also grant a score multiplier.
    The number of traps generated will match the selected difficulties.
    """

    display_name = "Difficulty Traps"

    option_disabled = 0
    option_enabled = 1
    default = 1

class MutatorTraps(Range):
    """
    How many mutator traps will be added to the item pool.
    Mutator traps cause every heist to roll 1 additional mutator,
    but also grant a score multiplier.
    """

    display_name = "Mutator Traps"

    range_start = 0
    range_end = 5
    default = 5

class ExcludedHeists(OptionSet):
    """
    If you're a COWARD that can't handle Bomb: Forest then you can exclude it here.
    Any heists you don't own will automatically be excluded.

    GROUPS:
    "Tutorials" = Stealth Tutorial, Loud Tutorial (only active with certain requirements, rare to get)
    "Stealth Only" = Stealth Tutorial, Shadow Raid, Murky Station, Yacht Heist
    "Events" = Cursed Kill Room, Prison Nightmare, Lab Rats, Safe House Nightmare
    "Endless" = Cursed Kill Room, Santa's Workshop, Prison Nightmare, Cook Off, White Xmas, Border Crystals, Lab Rats
    "Border Crossing" = Border Crossing, Border Crystals

    HEISTS:
    "Safe House Nightmare", "Lab Rats", "Bomb: Forest", "Goat Sim"
    """

    display_name = "Excluded Heists"

    valid_keys = ["Tutorials", "Stealth Only", "Events",
                  "Safe House Nightmare", "Bomb: Forest", "Goat Sim", "Border Crossing", "Lab Rats"]
    default = ["Events", "Border Crossing", "Bomb: Forest", "Goat Sim"]

# We must now define a dataclass inheriting from PerGameCommonOptions that we put all our options in.
# This is in the format "option_name_in_snake_case: OptionClassName".
@dataclass
class PAYDAY2Options(PerGameCommonOptions):
    score_checks: ScoreLocations
    starting_time: StartingTime
    time_upgrades: TimeUpgrades
    extra_time: TimeUpgradeStrength
    bot_count: BotCount
    second_saw: AdditionalSaw
    armor_unlocks: ArmorCount
    deployable_unlocks: DeployablesCount
    max_primary_weapons: PrimaryCount
    max_secondary_weapons: SecondaryCount
    max_melee_weapons: MeleeCount
    max_throwables: ThrowableCount
    starting_difficulty: MinDiff
    final_difficulty: MaxDiff
    one_down: OneDown
    difficulty_traps: DiffTraps
    mutator_traps: MutatorTraps
    excluded_heists: ExcludedHeists