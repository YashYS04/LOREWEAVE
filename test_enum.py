from enum import StrEnum
class CharacterStatus(StrEnum):
    active = "active"
    ACTIVE = "active"
print(CharacterStatus.active)
print(CharacterStatus.ACTIVE)
