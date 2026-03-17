from typing import NamedTuple
from enum import IntEnum
from BaseClasses import ItemClassification

class itemType(IntEnum):
    goal = 1
    progression = 2
    perkDeck = 3
    skill = 4
    weapon = 5
    filler = 6
    trap = 7
    unlock = 8

class itemData(NamedTuple):
    classification: ItemClassification
    count: int
    name: str
    type: itemType