from mazegen.config import MazeConfig
from mazegen.cell import Cell
import random
import time
import sys


class MazeGenerator:
    def __init__(self, config_path: str) -> None:
        self.property: MazeConfig = MazeConfig(config_path)
        self.grid: list[list[Cell]] = [
            [Cell(x, y) for x in range(self.property.width)]
            for y in range(self.property.height)
        ]
        sys.setrecursionlimit(10000)

        if self.property.seed:
            random.seed(self.property.seed)
        else:
            self.property.seed = random.randint(0, 999999)
            random.seed(self.property.seed)
        self._draw_42_pattern()

    def _draw_42_pattern(self) -> None:
        offset_x: int = (self.property.width - 7) // 2
        offset_y: int = (self.property.height - 5) // 2
        pattern_42: list[tuple[int, int]] = [
            (0, 0), (2, 0), (0, 1), (2, 1), (0, 2),
            (1, 2), (2, 2), (2, 3), (2, 4),
            (4, 0), (5, 0), (6, 0), (6, 1), (4, 2),
            (5, 2), (6, 2), (4, 3), (4, 4), (5, 4), (6, 4)
        ]
        for x, y in pattern_42:
            tx: int = offset_x + x
            ty: int = offset_y + y
            if ((tx, ty) == self.property.entry
                    or (tx, ty) == self.property.exit):
                raise ValueError("Entry / Exit coordinates overlap 42 pattern")
            self.grid[ty][tx].is_42 = True
            self.grid[ty][tx].visited = True
            self.grid[ty][tx].wals = 15

    def create_imperfect_loop(self) -> None:
        for y in range(self.property.height):
            for x in range(self.property.width):
                cell = self.grid[y][x]

                if cell.is_42:
                    continue
                closed_wall = sum([
                    cell.has_wall(Cell.north),
                    cell.has_wall(Cell.west),
                    cell.has_wall(Cell.east),
                    cell.has_wall(Cell.south)
                ])
                if closed_wall == 3:
                    if random.random() < 0.50:
                        options = []
                        if y > 0 and cell.has_wall(Cell.north):
                            options.append((0, 1, Cell.north, Cell.south))
                        if (y < self.property.height - 1 and
                                cell.has_wall(Cell.south)):
                            options.append((0, -1, Cell.south, Cell.north))
                        if (x > 0 and cell.has_wall(Cell.east)):
                            options.append((1, 0, Cell.east, Cell.west))
                        if (x < self.property.width - 1 and
                                cell.has_wall(Cell.west)):
                            options.append((-1, 0, Cell.west, Cell.east))
                        random.shuffle(options)
                        for dx, dy, dir_in, next_dir in options:
                            tx, ty = x + dx, y + dy
                            if not self.grid[y][x].is_42:
                                cell.remove_wall(dir_in)
                                self.grid[ty][tx].remove_wall(next_dir)
                                break

    def _make_maze_dfs(self,
                       x: int, y: int,
                       animate: bool, delay: float
                       ) -> None:
        self.grid[y][x].visited = True

        if animate:
            time.sleep(delay)

        options = [
            (0, -1, Cell.north, Cell.south)
            (0, 1, Cell.south, Cell.north)
            (1, 0, Cell.west, Cell.east)
            (-1, 0, Cell.east, Cell.west)
        ]
        random.shuffle(options)
        for dx, dy, dir_in, dir_out in options:
            tx = x + dx
            ty = y + dy

            if 0 <= tx < self.config.width and 0 <= ty < self.config.height:
                if not self.grid[ty][tx].visited:
                    self.grid[y][x].remove_wall(dir_in)
                    self.grid[ty][tx].remove_wall(dir_out)
                    self._make_maze_dfs(tx, ty, animate, delay)

    def dfs_generate(self, animate: bool = False, delay: float = 0.02) -> None:
        start_x: int = random.randint(0, self.property.width - 1)
        start_y: int = random.randint(0, self.property.height - 1)

        while self.grid[start_y][start_x].is_42:
            start_x: int = random.randint(0, self.property.width - 1)
            start_y: int = random.randint(0, self.property.height - 1)

        self._make_maze_dfs(start_x, start_y, animate, delay)

        if not self.property.perfect:
            self.create_imperfect_loop()

