from enum import Enum
from dataclasses import dataclass, field
from typing import List
import marshmallow_dataclass

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
    

@dataclass()
class ElectricityStateUpdate:
    state: str
    group: str
    devId: str = field(default=None)

@dataclass
class NotificationMessage:
    chat_id: str
    schedule_enabled: bool
    state_update: ElectricityStateUpdate
    groups: List[str] = field(default_factory=list)

ElectricityStateUpdateSchema = marshmallow_dataclass.class_schema(ElectricityStateUpdate)
NotificationMessageSchema = marshmallow_dataclass.class_schema(NotificationMessage)
