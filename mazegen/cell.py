class Cell:
    """
        Initialize the cells by adding
        the attributes x, y (position in the maze),
        walls (north, east, south, west),
        is visited (false by default), is_42 (false by default)

        methods:
            - remove_walls
            - has_wall
    """
    north: int = 1
    east: int = 2
    south: int = 4
    west: int = 8

    def __init__(self, x: int, y: int) -> None:
        self.x: int = x
        self.y: int = y
        self.walls: int = 15
        self.visited: bool = False
        self.is_42: bool = False

    def remove_wall(self, direction: int) -> None:
        """
            removes a wall according to the direction
        """
        self.walls &= ~direction

    def has_wall(self, direction: int) -> bool:
        """
            RReturns a boolean that tests whether
            a cell has a wall in a given direction.
        """
        return bool(self.walls & direction)
