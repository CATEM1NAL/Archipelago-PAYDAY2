from __future__ import annotations

from typing import TYPE_CHECKING

import math
from BaseClasses import Item, ItemClassification as IC
from .item_types import itemData, itemType

if TYPE_CHECKING:
    from .world import PAYDAY2World

progressionItemDict: dict[int, itemData] = {
    1: itemData(IC.progression | IC.useful, 5, "Extra Time", itemType.progression),
    2: itemData(IC.progression, 2, "Drill Speed", itemType.progression),
    3: itemData(IC.progression, 21, "Extra Bot", itemType.progression),
    4: itemData(IC.progression, 1, "Saw", itemType.progression),
    5: itemData(IC.progression, 1, "ECM", itemType.progression),
    6: itemData(IC.progression, 1, "Trip Mines", itemType.progression),
    7: itemData(IC.progression_deprioritized_skip_balancing, 35, "24 Coins", itemType.progression),
}

trapItemDict: dict[int, itemData] = {
    100: itemData(IC.trap, 5, "Difficulty Increase", itemType.trap),
    101: itemData(IC.trap, 5, "Additional Mutator", itemType.trap),
    102: itemData(IC.trap, 1, "One Down", itemType.trap),
}

fillerItemDict: dict[int, itemData] = {
    200: itemData(IC.useful, 62, "Primary Weapon", itemType.weapon),
    201: itemData(IC.useful, 28, "Secondary Weapon", itemType.weapon),
    202: itemData(IC.filler, 17, "Melee Weapon", itemType.weapon),
    203: itemData(IC.filler, 5, "Throwable", itemType.weapon),
    204: itemData(IC.filler, 1, "Second Saw", itemType.progression),
    205: itemData(IC.useful, 6, "Armor", itemType.unlock),
    206: itemData(IC.useful, 7, "Deployable", itemType.unlock),
    207: itemData(IC.useful, 115, "Random Skill", itemType.filler),
    208: itemData(IC.useful, 179, "Perk Deck Effect", itemType.filler),
    209: itemData(IC.filler, 150, "Stat Upgrade", itemType.filler),
    300: itemData(IC.filler, 0, "6 Coins", itemType.filler),
}

fillerCountDict: dict[int, int] = {
    200: 0, 201: 0, 202: 0, 203: 0, 204: 0, 205: 0, 206: 0, 207: 0, 208: 0, 209: 0,
}

itemDict: dict[int, itemData] = {}
itemDict.update(progressionItemDict)
itemDict.update(trapItemDict)
itemDict.update(fillerItemDict)

ITEM_NAME_TO_ID = {item.name: key for key, item in itemDict.items()}
itemKeys = []

class PAYDAY2Item(Item):
    game = "PAYDAY 2"

def update_items(world: PAYDAY2World) -> None:
    itemsForGoal = (60 - world.options.starting_time) / world.options.extra_time
    timeItemCap = (100 - world.options.starting_time) // world.options.extra_time
    numExtraTime = world.options.time_upgrades
    if numExtraTime < itemsForGoal:
        numExtraTime = math.ceil(itemsForGoal)
    elif numExtraTime > timeItemCap:
        numExtraTime = timeItemCap

    progressionItemDict[1] = itemData(IC.progression, numExtraTime, "Extra Time", itemType.progression)
    progressionItemDict[3] = itemData(IC.progression, world.options.bot_count, "Extra Bot", itemType.progression)

    trapItemDict[100] = itemData(IC.trap, world.options.difficulty_traps * (world.options.final_difficulty - world.options.starting_difficulty), "Difficulty Increase", itemType.trap)
    trapItemDict[101] = itemData(IC.trap, world.options.mutator_traps, "Additional Mutator", itemType.trap)
    if world.options.one_down != 1:
        trapItemDict[102] = itemData(IC.trap, 0, "One Down", itemType.trap)

    fillerItemDict[200] = itemData(IC.useful, world.options.max_primary_weapons, "Primary Weapon", itemType.weapon)
    fillerItemDict[201] = itemData(IC.useful, world.options.max_secondary_weapons, "Secondary Weapon", itemType.weapon)
    fillerItemDict[202] = itemData(IC.filler, world.options.max_melee_weapons, "Melee Weapon", itemType.weapon)
    fillerItemDict[203] = itemData(IC.filler, world.options.max_throwables, "Throwable", itemType.weapon)
    fillerItemDict[204] = itemData(IC.filler, world.options.second_saw, "Second Saw", itemType.progression)
    fillerItemDict[205] = itemData(IC.useful, world.options.armor_unlocks, "Armor", itemType.unlock)
    fillerItemDict[206] = itemData(IC.useful, world.options.deployable_unlocks, "Deployable", itemType.unlock)

def get_random_filler_item_name(world: PAYDAY2World) -> str:
    item = world.random.choice(tuple(fillerItemDict.values()))
    itemId = ITEM_NAME_TO_ID[item.name]
    if item.count > 0:
        if fillerCountDict[itemId] >= item.count:
            item = fillerItemDict[world.random.randint(300, 300)]
        fillerCountDict[itemId] += 1

    return item.name

def create_all_items(world: PAYDAY2World) -> None:
    #Create progression items
    itemPool: list[PAYDAY2Item] = []
    for itemId, item in progressionItemDict.items():
        for i in range(item.count):
            itemPool.append(world.create_item(item.name))

    for itemId, item in trapItemDict.items():
        for i in range(item.count):
            itemPool.append(world.create_item(item.name))

    unfilledLocations = len(world.multiworld.get_unfilled_locations(world.player))
    fillerCount = unfilledLocations - len(itemPool)

    itemPool += [world.create_filler() for _ in range(fillerCount)]

    world.multiworld.itempool += itemPool

    if world.options.starting_difficulty > 0:
        for i in range(world.options.starting_difficulty):
            world.push_precollected("Difficulty Increase")