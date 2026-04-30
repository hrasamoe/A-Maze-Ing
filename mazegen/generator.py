from .config import MazeConfig
from .cell import Cell
import random

class MazeGenerator:
    def __init__(self, config_path: str):
        self.config: MazeConfig = MazeConfig(config_path)
        self.grid: list[list[Cell]] = [
            [Cell(x, y) for x in range(self.config.width)]
            for y in range(self.config.height)
        ]

    def _embed_42_pattern(self) -> None:
        offset_x: int = (self.config.width - 7) // 2
        offset_y: int = (self.config.height - 5) // 2

        pattern_42: list[tuple[int, int]] = [
            (0, 0), (2, 0), (0, 1), (2, 1), (0, 2),
            (1, 2), (2, 2), (2, 3), (2, 4),
            (4, 0), (5, 0), (6, 0), (6, 1), (4, 2),
            (5, 2), (6, 2), (4, 3), (4, 4), (5, 4), (6, 4)
        ]

        for rel_x, rel_y in pattern_42:
            tx: int = offset_x + rel_x
            ty: int = offset_y + rel_y

            if (tx, ty) == self.config.entry or (tx, ty) == self.config.exit:
                raise ValueError(
                    "Entry/Exit coordinates overlap with '42' pattern."
                )

            self.grid[ty][tx].is_42 = True
            self.grid[ty][tx].visited = True
            self.grid[ty][tx].walls = 15

    def _crete_imperfect_way(self) -> None:
        for y in range(self.config.height):
            for x in range(self.config.width):
                cell = self.grid[y][x]

                if cell.is_42:
                    continue

                closed_walls = sum([
                    cell.has_wall(Cell.NORTH),
                    cell.has_wall(Cell.EAST),
                    cell.has_wall(Cell.SOUTH),
                    cell.has_wall(Cell.WEST)
                ])
                if closed_walls == 3:
                    if random.random() < 0.50:
                        options = []
                        if y > 0 and cell.has_wall(Cell.north):
                            options.append((0, -1, Cell.north, Cell.south))
                        if y < self.config.height - 1 and cell.has_wall(Cell.south):
                            options.append((0, 1, Cell.south, Cell.north))
                        if x > 0 and cell.has_wall(Cell.west):
                            options.append((-1, 0, Cell.west, Cell.east))
                        if x < self.config.width - 1 and cell.has_wall(Cell.east):
                            options.append((1, 0, Cell.east, Cell.west))
                        
                        random.shuffle(options)
                        for dx, dy, dir_out, next_dir_in in options:
                            tx, ty = x + dx, y + dy
                            if not self.grid[ty][tx].is_42:
                                cell.remove_wall(dir_out)
                                self.grid[ty][tx].remove_wall(next_dir_in)
                                break
