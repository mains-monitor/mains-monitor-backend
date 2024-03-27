from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Dict


class StrEnum(Enum):
    @staticmethod
    def _generate_next_value_(name, *args, **kwargs):
        return name

    def __hash__(self):
        return hash(self.value)

    def __str__(self):
        return str(self.value)

    def __eq__(self, other):
        if isinstance(other, str):
            return self.value == other
        elif isinstance(other, Enum):
            return self.value == other.value
        return super().__eq__(other)

    @classmethod
    def values(cls):
        return list(map(lambda c: c.value, cls))
    

@dataclass
class ElectricityStateUpdate:
    state: str
    group: str

@dataclass
class NotificationMessage:
    user_id: str
    groups: List[str]
    state_update: Dict[str, str]
    schedule_enabled: bool
