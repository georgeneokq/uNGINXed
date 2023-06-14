from dataclasses import dataclass
from typing import TypedDict


class Flagged(TypedDict):
    line: int
    column_start: int
    column_end: int
    directive: str


@dataclass
class SignatureResult:
    flagged: list[Flagged]
    reference: str
    additional_description: str
