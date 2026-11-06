import re
from dataclasses import dataclass
from typing import NewType, Self

from xid.xid import XID  # type: ignore[import-untyped]

_XID_PATTERN = re.compile(r"[0-9a-v]{19}[0g]")


@dataclass(frozen=True, slots=True)
class Xid:
    value: str

    def __post_init__(self) -> None:
        if _XID_PATTERN.fullmatch(self.value) is None:
            raise ValueError(f"Invalid XID: {self.value!r}")

    @classmethod
    def new(cls) -> Self:
        return cls(XID().string())

    @classmethod
    def parse(cls, value: str) -> Self:
        return cls(value)

    def __str__(self) -> str:
        return self.value


TeamId = NewType("TeamId", Xid)
PlayerId = NewType("PlayerId", Xid)
EventId = NewType("EventId", Xid)
OddsId = NewType("OddsId", Xid)
PredictionId = NewType("PredictionId", Xid)

ObjectId = TeamId | PlayerId | EventId | OddsId | PredictionId
