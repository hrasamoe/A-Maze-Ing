from .config import MazeConfig
from .cell import Cell
import random


class MazeGenerator:
    """
    Manages all operations related to maze generation:

    methods:
        - embed_42_pattern
        - transform_maze_to_hexa
        - create_imperfect_way
        - create_maze_with_bfs
        - create_maze_with_dfs
        - sofve_maze
        - get_path_coords
        - save_maze
    """

    def __init__(self, config_path: str):
        """
        Constructor of the MazeGenerator
        Get the config and set seed
        Initialize the 42 patern
        """

        self.config: MazeConfig = MazeConfig(config_path)
        self.grid: list[list[Cell]] = [
            [Cell(x, y) for x in range(self.config.width)]
            for y in range(self.config.height)
        ]
        self.config.seed = random.randint(0, 99999999)
        random.seed(self.config.seed)
        self._embed_42_pattern()

    def _embed_42_pattern(self) -> None:
        """
        Initialize each cell with the x, y coordinates
        of the exact position of each point in the 42 pattern.
        Test each point to see if the entry and exit points are not included.
        And set all cells to "visited".
        """

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

    def transform_maze_to_hexa(self) -> str:
        """
            Transform each wall into hexadecimal
        """

        result: str = ""
        for y in range(self.config.height):
            for x in range(self.config.width):
                result += f"{self.grid[y][x].walls:X}"
            result += '\n'
        return result

    def _crete_imperfect_way(self) -> None:
        """
            Remove wall of an cell if wall closed is more than 3
        """

        for y in range(self.config.height):
            for x in range(self.config.width):
                cell = self.grid[y][x]
                if cell.is_42:
                    continue
                closed_walls = sum([
                    cell.has_wall(Cell.north),
                    cell.has_wall(Cell.east),
                    cell.has_wall(Cell.south),
                    cell.has_wall(Cell.west)
                ])
                if closed_walls == 3:
                    if random.random() < 0.50:
                        options = []
                        if y > 0 and cell.has_wall(Cell.north):
                            options.append((0, -1, Cell.north, Cell.south))
                        if (y < self.config.width - 1
                                and cell.has_wall(Cell.south)):
                            options.append((0, 1, Cell.south, Cell.north))
                        if x > 0 and cell.has_wall(Cell.west):
                            options.append((-1, 0, Cell.west, Cell.east))
                        if (x < self.config.width - 1
                                and cell.has_wall(Cell.east)):
                            options.append((1, 0, Cell.east, Cell.west))

                        random.shuffle(options)
                        for dx, dy, dir_out, next_dir_in in options:
                            tx, ty = x + dx, y + dy
                            if ty < self.config.height and \
                                    tx < self.config.width:
                                if not self.grid[ty][tx].is_42:
                                    cell.remove_wall(dir_out)
                                    self.grid[ty][tx].remove_wall(next_dir_in)
                                    break

    def create_maze_with_bfs(self) -> None:
        """
            BFS (Breath First Search):
            Searches each node breadth-first. This means it searches all the
            neighbors of a node and marks
            it as visited, then searches all the
            neighbors of that neighbor, and so on.

            function-helper:
                - addfrontier
        """
        start_x: int = random.randint(0, self.config.width - 1)
        start_y: int = random.randint(0, self.config.height - 1)
        while self.grid[start_y][start_x].is_42:
            start_x = random.randint(0, self.config.width - 1)
            start_y = random.randint(0, self.config.height - 1)
        self.grid[start_y][start_x].visited = True
        frontier: list[tuple[int, int]] = []

        def add_frontier(x: int, y: int) -> None:
            """
                Store all the neighbors of the randomly
                chosen node in a frontier array
            """
            for dx, dy in [(0, -1), (1, 0), (0, 1), (-1, 0)]:
                tx, ty = x + dx, y + dy
                if (0 <= tx < self.config.width
                        and 0 <= ty < self.config.height):
                    if (not self.grid[ty][tx].visited
                            and (tx, ty) not in frontier):
                        frontier.append((tx, ty))
        add_frontier(start_x, start_y)
        while frontier:
            index: int = random.randint(0, len(frontier) - 1)
            dx, dy = frontier.pop(index)
            self.grid[dy][dx].visited = True
            maze_neighbors = []
            option: list[tuple[int, int, int, int]] = [
                (0, -1, Cell.north, Cell.south),
                (0, 1, Cell.south, Cell.north),
                (-1, 0, Cell.west, Cell.east),
                (1, 0, Cell.east, Cell.west),
            ]
            for ox, oy, dir_out, nex_dir_in in option:
                tx, ty = dx + ox, dy + oy
                if (0 <= tx < self.config.width
                        and 0 <= ty < self.config.height):
                    if (self.grid[ty][tx].visited and
                            not self.grid[ty][tx].is_42):
                        maze_neighbors.append((tx, ty, dir_out, nex_dir_in))
            if maze_neighbors:
                nx, ny, dir_out, nex_dir_in = random.choice(maze_neighbors)
                self.grid[dy][dx].remove_wall(dir_out)
                self.grid[ny][nx].remove_wall(nex_dir_in)
            add_frontier(dx, dy)

        if not self.config.perfect:
            self._crete_imperfect_way()

    def create_maze_with_dfs(self,) -> None:
        """
            DFS (Deep First Search):
            Deeper search: This means it randomly selects a node,
            then randomly selects
            one of its neighbors, marks it as a visit, then selects
            the hereditary node from that node, and so on.
        """
        start_x: int = random.randint(0, self.config.width - 1)
        start_y: int = random.randint(0, self.config.height - 1)
        while self.grid[start_y][start_x].is_42:
            start_x = random.randint(0, self.config.width - 1)
            start_y = random.randint(0, self.config.height - 1)
        self.grid[start_y][start_x].visited = True
        stack: list[tuple[int, int]] = [(start_x, start_y)]
        option: list[tuple[int, int, int, int]] = [
            (0, -1, Cell.north, Cell.south),
            (0, 1,  Cell.south, Cell.north),
            (-1, 0, Cell.west,  Cell.east),
            (1,  0, Cell.east,  Cell.west),
        ]
        while stack:
            cx, cy = stack[-1]
            neighbors = []
            for ox, oy, dir_out, dir_in in option:
                tx, ty = cx + ox, cy + oy
                if (0 <= tx < self.config.width
                        and 0 <= ty < self.config.height):
                    if (not self.grid[ty][tx].visited
                            and not self.grid[ty][tx].is_42):
                        neighbors.append((tx, ty, dir_out, dir_in))
            if neighbors:
                nx, ny, dir_out, dir_in = random.choice(neighbors)
                self.grid[cy][cx].remove_wall(dir_out)
                self.grid[ny][nx].remove_wall(dir_in)
                self.grid[ny][nx].visited = True
                stack.append((nx, ny))
            else:
                stack.pop()
        if not self.config.perfect:
            self._crete_imperfect_way()

    def solve_maze(
                    self,
                    start_x: int, start_y: int,
                    end_x: int, end_y: int) -> str:
        """
            Find the path from the entry point to the exit point.
            Test all possible path combinations up to the exit point.
            Store the possible cell values ​​leading to it in an array,
            removing the first element from the array at each iteration.
        """
        visited: set[tuple[int, int]] = set()
        visited.add((start_x, start_y))
        queue: list[tuple[int, int, str]] = [(start_x, start_y, "")]
        while queue:
            x, y, current_path = queue.pop(0)
            if x == end_x and y == end_y:
                return current_path
            options = [
                (0, -1, Cell.north, "N"),
                (1, 0, Cell.east, "E"),
                (0, 1, Cell.south, "S"),
                (-1, 0, Cell.west, "W")
            ]
            for dx, dy, wall_mask, dir_str in options:
                if not self.grid[y][x].has_wall(wall_mask):
                    tx, ty = x + dx, y + dy
                    if (tx, ty) not in visited:
                        visited.add((tx, ty))
                        queue.append((tx, ty, current_path + dir_str))
        return ""

    def _get_path_coords(
        self, start_x: int, start_y: int, path_str: str
    ) -> set[tuple[int, int]]:
        """
            Retrieve the coordinates of the solver
            to transform it into a tuple list (x, y)
        """
        coords: set[tuple[int, int]] = set()
        cx, cy = start_x, start_y
        for move in path_str:
            if move == 'N':
                cy -= 1
            elif move == 'S':
                cy += 1
            elif move == 'E':
                cx += 1
            elif move == 'W':
                cx -= 1
            coords.add((cx, cy))
        return coords

    def save_maze(self) -> None:
        """
            Write the entry and exit points,
            the hexadecimal representation of the maze,
            and the solution to the maze in a maze_output.txt file.
        """
        try:
            with open(self.config.output_file, 'w') as fd:
                fd.write(self.transform_maze_to_hexa().strip() + '\n')
                fd.write('\n')
                ex, ey = self.config.entry
                xx, xy = self.config.exit
                fd.write(f"{ex}, {ey}\n")
                fd.write(f"{xx}, {xy}\n")
                solution = self.solve_maze(ex, ey, xx, xy)
                fd.write(f"{solution}\n")
        except OSError as e:
            raise Exception(
                "An Error was occured"
                f"{e}"
            )
