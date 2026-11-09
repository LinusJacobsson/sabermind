import re
from dataclasses import dataclass
from typing import ClassVar, Self

from xid.xid import XID  # type: ignore[import-untyped]

_XID_PATTERN = re.compile(r"[0-9a-v]{19}[0g]")


@dataclass(frozen=True, slots=True)
class Xid:
    value: str
    prefix: ClassVar[str] = ""

    def __post_init__(self) -> None:
        prefix, separator, suffix = self.value.partition("_")
        if (
            not self.prefix
            or separator != "_"
            or prefix != self.prefix
            or _XID_PATTERN.fullmatch(suffix) is None
        ):
            raise ValueError(f"Invalid {type(self).__name__}: {self.value!r}")

    @classmethod
    def new(cls) -> Self:
        return cls(f"{cls.prefix}_{XID().string()}")

    @classmethod
    def parse(cls, value: str) -> Self:
        return cls(value)

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class TeamId(Xid):
    prefix: ClassVar[str] = "team"


@dataclass(frozen=True, slots=True)
class PlayerId(Xid):
    prefix: ClassVar[str] = "player"


@dataclass(frozen=True, slots=True)
class EventId(Xid):
    prefix: ClassVar[str] = "event"


@dataclass(frozen=True, slots=True)
class OddsId(Xid):
    prefix: ClassVar[str] = "odds"


@dataclass(frozen=True, slots=True)
class SimulationId(Xid):
    prefix: ClassVar[str] = "sim"


type ObjectId = TeamId | PlayerId | EventId | OddsId | SimulationId
