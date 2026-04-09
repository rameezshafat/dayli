from dataclasses import dataclass


@dataclass(slots=True)
class Constraint:
    name: str
    value: str

