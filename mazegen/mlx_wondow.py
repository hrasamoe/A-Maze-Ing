from mlx import Mlx
from mazegen import colors
from mazegen.config import MazeConfig
from mazegen.cell import Cell
from mazegen.generator import MazeGenerator
import random
import ctypes
import os
import time

class Renderer:
    def __init__(self, w: int = 1200, h: int = 800, config_path: str = "config.txt") -> None:
        self.maze: MazeGenerator = MazeGenerator(config_path)
        self.config_path = config_path
        self.w: int = self.maze.config.window_w
        self.h: int = self.maze.config.window_h
        self.mlx: Mlx = Mlx()
        self.mlx_ptr: ctypes.c_void_p = self.mlx.mlx_init()
        self.win: ctypes.c_void_p = self.mlx.mlx_new_window(
            self.mlx_ptr, self.w, self.h, "Formes")
        self.img: ctypes.c_void_p = self.mlx.mlx_new_image(
            self.mlx_ptr, self.w, self.h)
        self.data: memoryview
        self.bpp: int
        self.sl: int
        self.data, self.bpp, self.sl, _ = \
            self.mlx.mlx_get_data_addr(self.img)
        self.bpp = self.bpp // 8
        #initialisation labyrinth


    def put_pixel(self, x: int, y: int, color: int) -> None:
        if 0 <= x < self.w and 0 <= y < self.h:
            off: int = y * self.sl + x * (self.bpp)
            self.data[off:off+self.bpp] = color.to_bytes(self.bpp, 'little')

    def draw_square(
        self, x: int, y: int, size: int, color: int
    ) -> None:
        """Carré plein de côté `size` avec coin supérieur gauche en (x, y)."""
        for row in range(y, y + size):
            for col in range(x, x + size):
                self.put_pixel(col + x, row + y, color)

    def draw_rect(
        self, x: int, y: int,
        rect_w: int, rect_h: int, color: int
    ) -> None:
        """Rectangle plein width×height,
        coin supérieur gauche en (x, y).
        """
        for row in range(y, y + rect_h):
            for col in range(x, x + rect_w):
                self.put_pixel(col, row, color)

    def _fill_rect(self,
               x: int, y: int,
               w: int, h: int,
               color: int) -> None:
        for dy in range(h):
            for dx in range(w):
                self.put_pixel(x + dx, y + dy, color)

    def draw_square_outline(
        self, x: int, y: int, size: int,
        thickness: int, color: int
    ) -> None:
        """Contour d'un carré avec épaisseur de trait."""
        for t in range(thickness):
            for i in range(size):
                self.put_pixel(x + i, y + t, color)
                self.put_pixel(x + i, y + size - 1 - t, color)
                self.put_pixel(x + t, y + i, color)
                self.put_pixel(x + size - 1 - t, y + i, color)

    def text(self, x: int, y: int, color: int, s: str) -> None:
        """Affiche du texte dans la fenêtre (pas dans le buffer image)."""
        self.mlx.mlx_string_put(self.mlx_ptr, self.win, x, y, color, s)

    def flush(self) -> None:
        """Envoie le buffer image vers la fenêtre."""
        self.mlx.mlx_put_image_to_window(
            self.mlx_ptr, self.win, self.img, 0, 0)

    #draw42
    def _embed_42_pattern(self, config: dict[str, int], color: int) -> None:
        offset_x: int = (self.maze.config.width - 7) // 2
        offset_y: int = (self.maze.config.height - 5) // 2

        pattern_42: list[tuple[int, int]] = [
            (0, 0), (2, 0), (0, 1), (2, 1), (0, 2),
            (1, 2), (2, 2), (2, 3), (2, 4),
            (4, 0), (5, 0), (6, 0), (6, 1), (4, 2),
            (5, 2), (6, 2), (4, 3), (4, 4), (5, 4), (6, 4)
        ]

        for rel_x, rel_y in pattern_42:
            tx: int = offset_x + rel_x
            ty: int = offset_y + rel_y

            if (tx, ty) == self.maze.config.entry or (tx, ty) == self.maze.config.exit:
                raise ValueError(
                    "Entry/Exit coordinates overlap with '42' pattern."
                )

            self.maze.grid[ty][tx].is_42 = True
            self.maze.grid[ty][tx].visited = True
            self.maze.grid[ty][tx].walls = 15

    
    #draw maze
    def create_maze_with_bfs(
                                self,
                                animate: bool = False,
                                delay: float = 0.02) -> None:
        start_x: int = random.randint(0, self.maze.config.width - 1)
        start_y: int = random.randint(0, self.maze.config.height - 1)
        while self.maze.grid[start_y][start_x].is_42:
            start_x = random.randint(0, self.maze.config.width - 1)
            start_y = random.randint(0, self.maze.config.height - 1)
        self.maze.grid[start_y][start_x].visited = True
        frontier: list[tuple[int, int]] = []
        def add_frontier(x: int, y: int) -> None:
            for dx, dy in [(0, -1), (1, 0), (0, 1), (-1, 0)]:
                tx, ty = x + dx, y + dy
                if (0 <= tx < self.maze.config.width
                        and 0 <= ty < self.maze.config.height):
                    if (not self.maze.grid[ty][tx].visited
                            and (tx, ty) not in frontier):
                        frontier.append((tx, ty))
        add_frontier(start_x, start_y)
        while frontier:
            index: int = random.randint(0, len(frontier) - 1)
            dx, dy = frontier.pop(index)
            self.maze.grid[dy][dx].visited = True
            maze_neighbors = []
            option: list[tuple[int, int, int, int]] = [
                (0, -1, Cell.north, Cell.south),
                (0, 1, Cell.south, Cell.north),
                (-1, 0, Cell.west, Cell.east),
                (1, 0, Cell.east, Cell.west),
            ]
            for ox, oy, dir_out, nex_dir_in in option:
                tx, ty = dx + ox, dy + oy
                if (0 <= tx < self.maze.config.width
                        and 0 <= ty < self.maze.config.height):
                    if (self.maze.grid[ty][tx].visited and
                            not self.maze.grid[ty][tx].is_42):
                        maze_neighbors.append((tx, ty, dir_out, nex_dir_in))
            if maze_neighbors:
                nx, ny, dir_out, nex_dir_in = random.choice(maze_neighbors)
                self.maze.grid[dy][dx].remove_wall(dir_out)
                self.maze.grid[ny][nx].remove_wall(nex_dir_in)
            add_frontier(dx, dy)
        if not self.maze.config.perfect:
            self._crete_imperfect_way()

    def render_terminal(self,
                player_pos: tuple[int, int] | None = None,
                solution_mode: int = 0) -> None:
        #animation
        state: dict = {
            't_last':  time.time(),  # timestamp de la dernière frame
            'elapsed': 0.0,           # temps total écoulé en secondes
            'x':       float(W / 2),  # position X du centre du carré
            'y':       float(H / 2),  # position Y
            'vx':      200.0,         # vitesse X en pixels / seconde
            'vy':      150.0,         # vitesse Y en pixels / seconde
            'angle':   0.0,           # rotation (pour des effets avancés)
        }
        now: float = time.time()
        dt: float = min(now - s['t_last'], 0.05)
        s['t_last'] = now
        s['elpased'] += dt
        #animation
        px, py = player_pos if player_pos else self.maze.config.entry
        ex, ey = self.maze.config.exit
        solution: set[tuple[int, int]] = set()

        # Calcul dynamique de la taille d'une cellule selon la fenêtre
        cell_w: int = self.maze.config.window_w // self.maze.config.width
        cell_h: int = (self.maze.config.window_h - 150) // self.maze.config.height
        wall_t: int = max(2, min(cell_w, cell_h) // 8)

        if solution_mode == 1:
            path_str = self.solve_maze(px, py, ex, ey)
            solution = self._get_path_coords(px, py, path_str)

        for y in range(self.maze.config.height):
            for x in range(self.maze.config.width):
                cell: Cell = self.maze.grid[y][x]
                cx = x * cell_w
                cy = y * cell_h

                # Fond
                if (x, y) == (px, py):
                    bg = colors.MLX_WHITE
                elif (x, y) == self.maze.config.entry:
                    bg = colors.MLX_YELLOW
                elif (x, y) == self.maze.config.exit:
                    bg = colors.MLX_BLUE
                elif (x, y) in solution:
                    bg = colors.MLX_YELLOW
                elif cell.is_42:
                    bg = colors.MLX_GREEN
                else:
                    bg = colors.MLX_BLACK
                self._fill_rect(cx, cy, cell_w, cell_h, bg)
                # Murs — cell_w/cell_h complets pour boucher les coins
                if cell.has_wall(Cell.north):
                    self._fill_rect(cx, cy, cell_w, wall_t, colors.MLX_WHITE)
                if cell.has_wall(Cell.south):
                    self._fill_rect(cx, cy + cell_h - wall_t, cell_w, wall_t, colors.MLX_WHITE)
                if cell.has_wall(Cell.west):
                    self._fill_rect(cx, cy, wall_t, cell_h, colors.MLX_WHITE)
                if cell.has_wall(Cell.east):
                    self._fill_rect(cx + cell_w - wall_t, cy, wall_t, cell_h, colors.MLX_WHITE)
        

    def draw_menu(self):
        self.text(0, self.maze.config.window_h - 50, colors.MLX_WHITE, "Menu:")

    def draw_new_maze(self):
        # self._fill_rect(0, 0, self.w, self.h, colors.MLX_BLACK)  # efface
        self.data[0:self.sl*self.maze.config.window_h] = b'\x00\x00\x00\xff' * (self.sl * self.maze.config.window_h // self.bpp)
        self.maze = MazeGenerator(self.config_path)
        self.create_maze_with_bfs()
        self.render_terminal()

    def draw_menu(self, color: int):
        pos_y = self.maze.config.window_h - 150
        pos_x = 50
        self.text(pos_x, pos_y, color, "1. Regenerate Maze [W]")
        self.text(pos_x, pos_y + 15, color, f"2. Animation: ON")
        self.text(pos_x, pos_y + 30, color, "3. Show the shortest path solution")
        self.text(pos_x, pos_y + 45, color, "4. Hide Solution Path")
        self.text(pos_x, pos_y + 60, color, "5. Change Wall Color")
        self.text(pos_x, pos_y + 75, color, f"6. Toggle Perfect Maze")
        self.text(pos_x, pos_y + 90, color, f"7. Save maze to File")
        self.text(pos_x, pos_y + 105, color, "8. Quit The Game [echap]")
    
    def on_key_pressed(self, keycode: int, param: object):
        if keycode == 119: #w
            self.draw_new_maze()
            
        if keycode == 97: #a
            print("a cliked")
        if keycode == 115: #s
            print("s cliked")
        if keycode == 100: #d
            print("d cliked")
        if keycode == 65307:
            self.mlx.mlx_loop_exit(self.mlx_ptr)
        self.draw_menu(colors.MLX_RED)
        self.flush()
    def run(self) -> None:
        try:
            config = {
                "entry": (0,0),
                "exit": (5,8),
                "width": self.w,
                "height": self.h
            }
            
            self._embed_42_pattern(config, 0xFF7C6AF7)
            self.draw_new_maze()
            # tout afficher d'un coup
            self.flush()
            self.mlx.mlx_key_hook(self.win, self.on_key_pressed, None)
            self.mlx.mlx_hook(self.win, 33, 0,
                lambda d: self.mlx.mlx_loop_exit(self.mlx_ptr), None)
            self.mlx.mlx_loop(self.mlx_ptr)
        except Exception as e:
            print(f"An error occured : {e}")
        finally:
            self.mlx.mlx_destroy_window(self.mlx_ptr, self.win)
            self.mlx.mlx_release(self.mlx_ptr)

