from __future__ import annotations

from typing import TYPE_CHECKING

import worlds.payday2.options
from BaseClasses import Item, ItemClassification as IC
from .item_types import itemData, itemType

if TYPE_CHECKING:
    from .world import PAYDAY2World

progressionItemDict: dict[int, itemData] = {
    1: itemData(IC.progression, 5, "Extra Time", itemType.progression),
    2: itemData(IC.progression, 2, "Drill Speed", itemType.progression),
    3: itemData(IC.progression, 21, "Extra Bot", itemType.progression),
    4: itemData(IC.progression, 1, "First Saw", itemType.progression),
    5: itemData(IC.progression, 1, "ECM", itemType.progression),
    6: itemData(IC.progression, 1, "Trip Mines", itemType.progression),
}

trapItemDict: dict[int, itemData] = {
    100: itemData(IC.trap, 5, "Difficulty Increase", itemType.trap),
    101: itemData(IC.trap, 5, "Additional Mutator", itemType.trap),
}

fillerItemDict: dict[int, itemData] = {
    200: itemData(IC.useful, 62, "Primary Weapon", itemType.weapon),
    201: itemData(IC.useful, 28, "Secondary Weapon", itemType.weapon),
    202: itemData(IC.filler, 17, "Melee Weapon", itemType.weapon),
    203: itemData(IC.filler, 5, "Throwable", itemType.weapon),
    204: itemData(IC.filler, 1, "Second Saw", itemType.progression),
    205: itemData(IC.useful, 6, "Armor", itemType.unlock),
    206: itemData(IC.useful, 7, "Deployable", itemType.unlock),
    300: itemData(IC.useful, 0, "Random Skill", itemType.filler),
    301: itemData(IC.useful, 0, "Perk Deck Effect", itemType.filler),
    302: itemData(IC.filler, 0, "Stat Upgrade", itemType.filler),
}

fillerCountDict: dict[int, int] = {
    200: 0,
    201: 0,
    202: 0,
    203: 0,
    204: 0,
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
    progressionItemDict[3] = itemData(IC.progression, world.options.bot_count, "Extra Bot", itemType.progression)

def get_random_filler_item_name(world: PAYDAY2World) -> str:
    item = world.random.choice(tuple(fillerItemDict.values()))
    itemId = ITEM_NAME_TO_ID[item.name]
    if item.count > 0:
        if fillerCountDict[itemId] >= item.count:
            item = fillerItemDict[world.random.randint(300, 302)]
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