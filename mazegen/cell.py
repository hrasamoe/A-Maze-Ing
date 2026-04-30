class Cell:
    north: int = 8
    east: int = 4
    south: int = 2
    west: int = 1

    def __init__(self, x: int, y: int) -> None:
        self.x: int = x
        self.y: int = y
        self.walls: int = 15
        self.visited: bool = False
        self.is_42: bool = False

    def remove_wall(self, direction: int) -> None:
        self.walls &= ~direction

    def has_wall(self, direction: int) -> bool:
        return bool(self.walls & direction)
