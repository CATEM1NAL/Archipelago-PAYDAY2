from __future__ import annotations
from rule_builder.rules import Has, HasAllCounts
from worlds.generic.Rules import forbid_item

from typing import TYPE_CHECKING
from BaseClasses import ItemClassification, Location, Region, LocationProgressType
from . import items

if TYPE_CHECKING:
    from .world import PAYDAY2World

def triangle(n: int) -> int:
    return n * (n + 1) // 2

maxScoreLocations = (200) + 1
LOCATION_NAME_TO_ID = { f"{triangle(i)} Crime Points" : i for i in range(1, maxScoreLocations) }

safehouseRooms = ["Scarface's Room", "Dallas' Office", "Hoxton's Files", "Clover's Surveillance Center",
                 "Duke's Gallery", "Houston's Workshop", "Sydney's Studio", "Rust's Corner", "Joy's Van",
                     "h3h3", "Bonnie's Gambling Den", "Jiro's Lounge", "Common Rooms", "Jimmy's Bar",
               "Sangres' Cave", "Chains' Weapons Workshop", "Bodhi's Surfboard Workshop", "Jacket's Hangout",
                 "Sokol's Hockey Gym", "Dragan's Gym", "Vault", "Wolf's Workshop", "Wick's Shooting Range"]

LOCATION_NAME_TO_ID.update({f"{room} - Tier 2": key + maxScoreLocations for key, room in enumerate(safehouseRooms)})
LOCATION_NAME_TO_ID.update({f"{room} - Tier 3": key + maxScoreLocations + len(safehouseRooms) for key, room in enumerate(safehouseRooms)})
LOCATION_NAME_TO_ID.update({f"Heist {i} Completed": i + maxScoreLocations + 2 * len(safehouseRooms) for i in range(1, 7)})

class PAYDAY2Location(Location):
    game = "PAYDAY 2: Criminal Dawn"

def create_and_connect_regions(world: PAYDAY2World) -> None:
    world.multiworld.regions.append(Region("Crime.net", world.player, world.multiworld))
    world.multiworld.regions.append(Region("Safe House Tier 2", world.player, world.multiworld))
    world.multiworld.regions.append(Region("Safe House Tier 3", world.player, world.multiworld))

    crimenet = world.get_region("Crime.net")
    safehouseT2 = world.get_region("Safe House Tier 2")
    safehouseT3 = world.get_region("Safe House Tier 3")
    itemsForGoal = (60 - world.timeBonusStrength) / world.timeBonusStrength

    for i in range(1, 7):
        world.multiworld.regions.append(Region(f"Heist {i}", world.player, world.multiworld))
        heistRegion = world.get_region(f"Heist {i}")
        locName = f"Heist {i} Completed"
        locId = world.location_name_to_id[locName]
        if i == 6: locId = None
        location = PAYDAY2Location(world.player, locName, locId, heistRegion)
        location.progress_type = LocationProgressType.PRIORITY
        heistRegion.locations.append(location)
        itemsForConnection = round((i - 1) * (itemsForGoal / 5))

        if i == 1: world.create_entrance(crimenet, heistRegion,None,"Start Run")
        else: world.create_entrance(world.get_region(f"Heist {i - 1}"), heistRegion, Has("Time Bonus", itemsForConnection), f"Heist {i - 1} Completed")

    world.create_entrance(crimenet, safehouseT2, None, "276 Coins") #HasAllCounts({"24 Coins": 12, "Time Bonus": itemsForGoal // 3}),
    world.create_entrance(safehouseT2, safehouseT3, None, "828 Coins") #HasAllCounts({"24 Coins": 35, "Time Bonus": 2 * itemsForGoal // 3}),

def create_all_locations(world: PAYDAY2World) -> None:
    create_score_locations(world)

def create_score_locations(world: PAYDAY2World) -> None:
    # Create regions, assign a location to each region, chain entrances together
    for i in range(2,4):
        safehouse = world.get_region(f"Safe House Tier {i}")
        for room in safehouseRooms:
            locName = f"{room} - Tier {i}"
            locId = world.location_name_to_id[locName]
            location = PAYDAY2Location(world.player, locName, locId, safehouse)
            location.progress_type = LocationProgressType.EXCLUDED
            safehouse.locations.append(location)
            forbid_item(location, "24 Coins", world.player)
            forbid_item(location, "6 Coins", world.player)

    firstHeist = world.get_region("Crime.net")

    requiredTimeBonuses = {}
    for i in range(1, world.options.score_checks+1):
        locName = f"{triangle(i)} Crime Points"
        locId = world.location_name_to_id[locName]

        region = Region(locName, world.player, world.multiworld)
        world.multiworld.regions.append(region)

        location = PAYDAY2Location(world.player, locName, locId, region)
        region.locations.append(location)

        itemsForGoal = (60 - world.timeBonusStrength) / world.timeBonusStrength
        bots = i // (world.options.score_checks // world.botCount)

        if i == 1:
            firstHeist.connect(region, "1 point")

        else:
            if i < 4 * (world.options.score_checks / (itemsForGoal - 1)):
                timeBonuses = round(i / (world.options.score_checks / (itemsForGoal - 1)))
                requiredTimeBonuses.update({triangle(i): timeBonuses})

            elif 4 * (world.options.score_checks / (itemsForGoal - 1)) <= i < world.options.score_checks:
                timeBonuses =  round(i / (world.options.score_checks / (itemsForGoal - 1)))
                #print(i // (world.options.score_checks // itemsForGoal - 1))
                requiredTimeBonuses.update({triangle(i): timeBonuses})

            elif i == world.options.score_checks:
                #timeBonuses = round(i / (world.options.score_checks / itemsForGoal))
                timeBonuses = itemsForGoal
                requiredTimeBonuses.update({triangle(i): timeBonuses})

            else:
                timeBonuses = 0
                requiredTimeBonuses.update({triangle(i): 0})

            #print(f"{location.name}: {timeBonuses}")
            locationRule = HasAllCounts({"Time Bonus": timeBonuses,
                                         "Extra Bot": bots,
                                         "Perma-Perk": i // (world.options.score_checks // 8),
                                         "Perma-Skill": i // (world.options.score_checks // 8)})

            world.set_rule(location, locationRule)

        if i > 1:
            prevRegion.connect(region, f"{i} points")
        prevRegion = region

    required = 0
    prevScore = 0
    world.locationToScoreCap = []
    for score, timeBonuses in requiredTimeBonuses.items():
        if timeBonuses > required:
            world.locationToScoreCap.append(prevScore)
            required += 1
        prevScore = score
    #print(world.locationToScoreCap)

    location = world.get_location("Heist 6 Completed")
    locationRule = HasAllCounts({"Time Bonus": itemsForGoal,
                                 "Extra Bot": world.botCount,
                                 "Perma-Perk": 8,
                                 "Perma-Skill": 8})

    world.set_rule(location, locationRule)

    victory = items.PAYDAY2Item("Victory", ItemClassification.progression, None, world.player)
    location.place_locked_item(victory)

    world.set_completion_rule(Has("Victory"))