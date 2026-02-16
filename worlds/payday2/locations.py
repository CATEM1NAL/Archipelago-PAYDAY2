from __future__ import annotations
from worlds.generic.Rules import set_rule

from math import floor
from typing import TYPE_CHECKING
from BaseClasses import ItemClassification, Location, Region
from . import items

if TYPE_CHECKING:
    from .world import PAYDAY2World

def triangle(n: int) -> int:
    return n * (n + 1) // 2
LOCATIONCOUNT = 100
LOCATION_NAME_TO_ID = { f"{triangle(i)} Crime Points" : i for i in range(1, LOCATIONCOUNT+1) }

class PAYDAY2Location(Location):
    game = "PAYDAY 2"

def create_and_connect_regions(world: PAYDAY2World) -> None:
    world.multiworld.regions.append(Region("Crime.net", world.player, world.multiworld))

def create_all_locations(world: PAYDAY2World) -> None:
    create_score_locations(world)

def create_score_locations(world: PAYDAY2World) -> None:
    # Create regions, assign a location to each region, chain entrances together
    crimenet = world.get_region("Crime.net")
    for i in range(1, LOCATIONCOUNT+1):
        locName = f"{triangle(i)} Crime Points"
        locId = world.location_name_to_id[locName]

        region = Region(locName, world.player, world.multiworld)
        world.multiworld.regions.append(region)

        location = PAYDAY2Location(world.player, locName, locId, region)
        region.locations.append(location)

        if i == 1:
            crimenet.connect(region, "Start run")
        else:
            if i % floor(LOCATIONCOUNT/5) == 0:
                prevRegion.connect(region, f"{triangle(i) - triangle(i - 1)} points", lambda state, count=i // floor(LOCATIONCOUNT/5): state.has("Extra Time", world.player, count))
            else:
                prevRegion.connect(region, f"{triangle(i) - triangle(i - 1)} points")
        prevRegion = region

    locName = "Final Heist Completed"
    region = Region(locName, world.player, world.multiworld)
    location = PAYDAY2Location(world.player, locName, None, region)
    set_rule(location, lambda state, count=5: state.has("Extra Time",world.player, count))
    region.locations.append(location)
    crimenet.connect(region, f"Final Heist")

    victory = items.PAYDAY2Item("Victory", ItemClassification.progression, None, world.player)
    location.place_locked_item(victory)

    world.multiworld.completion_condition[world.player] = lambda state: state.has("Victory", world.player)