from __future__ import annotations

from typing import TYPE_CHECKING

import math
from BaseClasses import Item, ItemClassification as IC
from .item_types import itemData, itemType

if TYPE_CHECKING:
    from .world import PAYDAY2World

progressionItemDict: dict[int, itemData] = {
    1: itemData(IC.progression | IC.useful, 0, "Time Bonus", itemType.progression),
    2: itemData(IC.progression, 2, "Drill Sawgeant", itemType.progression),
    3: itemData(IC.progression, 3, "Extra Bot", itemType.progression),
    4: itemData(IC.progression, 2, "Nine Lives", itemType.progression),
    5: itemData(IC.progression, 8, "Perma-Perk", itemType.progression),
    6: itemData(IC.progression, 8, "Perma-Skill", itemType.progression)
}

trapItemDict: dict[int, itemData] = {
}

usefulItemDict: dict[int, itemData] = {
    200: itemData(IC.useful, 38, "24 Coins", itemType.progression),
    201: itemData(IC.useful, 2, "OVE9000 Saw", itemType.unlock),
    202: itemData(IC.useful, 1, "ECM", itemType.unlock),
    203: itemData(IC.useful, 1, "Trip Mines", itemType.unlock),
    204: itemData(IC.useful, 13, "Skill", itemType.filler),
    205: itemData(IC.useful, 13, "Perk", itemType.filler),
}

fillerItemDict: dict[int, itemData] = {
    300: itemData(IC.filler, 18, "Primary Weapon", itemType.weapon),
    301: itemData(IC.filler, 41, "Akimbo", itemType.weapon),
    302: itemData(IC.filler, 23, "Secondary Weapon", itemType.weapon),
    303: itemData(IC.filler, 18, "Melee Weapon", itemType.weapon),
    304: itemData(IC.filler, 5, "Throwable", itemType.weapon),
    305: itemData(IC.filler, 6, "Armor", itemType.unlock),
    306: itemData(IC.filler, 7, "Deployable", itemType.unlock),
    307: itemData(IC.filler, 10, "Stat Boost", itemType.filler)
}

infFillerItemDict: dict[int, itemData] = {
    400: itemData(IC.filler, 0, "6 Coins", itemType.filler)
}

fillerLimitDict: dict[int, int] = {
    300: 18,
    301: 41,
    302: 23,
    303: 18,
    304: 5,
    305: 6,
    306: 7,
    307: 100
}

itemDict: dict[int, itemData] = {}
itemDict.update(progressionItemDict)
itemDict.update(trapItemDict)
itemDict.update(usefulItemDict)
itemDict.update(fillerItemDict)
itemDict.update(infFillerItemDict)

ITEM_NAME_TO_ID = {item.name: key for key, item in itemDict.items()}
itemKeys = []

class PAYDAY2Item(Item):
    game = "PAYDAY 2: Criminal Dawn"

def update_items(world: PAYDAY2World) -> None:
    progressionItemDict[1] = itemData(itemDict[1][0], world.maxTimeBonuses, *itemDict[1][2:])
    print(f"{world.player_name} has {world.maxTimeBonuses} Time Bonus items.")
    progressionItemDict[3] = itemData(itemDict[3][0], world.botCount, *itemDict[3][2:])
    progressionItemDict[4] = itemData(itemDict[4][0], world.options.saws, *itemDict[4][2:])

    optList = [world.options.primary_weapons, #300
               world.options.akimbo, #301
               world.options.secondary_weapons, #302
               world.options.melee_weapons, #303
               world.options.throwables] #304

    for i, opt in enumerate(optList):
        fillerItemDict[300+i] = itemData(itemDict[300+i][0], opt.value, *itemDict[300+i][2:])
        fillerLimitDict[300+i] -= opt

def get_random_filler_item_name(world: PAYDAY2World) -> str:
    fillerType = world.random.choice(["weapon", "upgrade"])
    if fillerType == "weapon": item = fillerItemDict[world.random.randint(300, 304)]
    elif fillerType == "upgrade": item = fillerItemDict[world.random.randint(305, 307)]

    itemId = ITEM_NAME_TO_ID[item.name]

    if fillerLimitDict[itemId] > 0: fillerLimitDict[itemId] -= 1
    else: item = world.random.choice(tuple(infFillerItemDict.values()))

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

    for itemId, item in usefulItemDict.items():
        for i in range(item.count):
            itemPool.append(world.create_item(item.name))

    for itemId, item in fillerItemDict.items():
        for i in range(item.count):
            itemPool.append(world.create_item(item.name))

    unfilledLocations = len(world.multiworld.get_unfilled_locations(world.player))
    fillerCount = unfilledLocations - len(itemPool)

    progressionItemDict[3] = itemData(itemDict[3][0], world.botCount, *itemDict[3][2:])

    itemPool += [world.create_filler() for _ in range(fillerCount)]

    world.multiworld.itempool += itemPool