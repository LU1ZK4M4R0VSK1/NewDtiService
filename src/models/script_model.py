from dataclasses import dataclass

@dataclass
class Script:
    id: int
    name: str
    category: str
    path: str
    description: str
    windows_only: bool = False

    @staticmethod
    def from_tuple(data):
        return Script(
            id=data[0],
            name=data[1],
            category=data[2],
            path=data[3],
            description=data[4],
            windows_only=bool(data[5])
        )