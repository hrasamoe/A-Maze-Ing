from mlx import Mlx  # type: ignore
from mazegen import colors
from mazegen.cell import Cell
from mazegen.generator import MazeGenerator
import random
import ctypes
import time
import math


class Renderer:
    def __init__(
                self, w: int = 1200, h: int = 800,
                config_path: str = "config.txt") -> None:
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
        total = self.maze.config.width * self.maze.config.height
        self.s: dict = {
                't_last':  time.time(),  # timestamp de la dernière frame
                'elapsed': 0.0,           # temps total écoulé en secondes
                'x':       0,  # position X du centre du carré
                'y':       0,  # position Y
                'vx':      200.0,         # vitesse X en pixels / seconde
                'vy':      150.0,         # vitesse Y en pixels / seconde
                'angle':   0.0,
                'count': 0,
                'reveal_order': random.sample(range(total), total)
                }
        self.wall_color = colors.MLX_WHITE
        self.toggle_solution = False

    def put_pixel(self, x: int, y: int, color: int) -> None:
        if 0 <= x < self.w and 0 <= y < self.h:
            off: int = y * self.sl + x * (self.bpp)
            self.data[off:off+self.bpp] = color.to_bytes(self.bpp, 'little')

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

    def _fill_rect(
                self, x: int, y: int,
                w: int, h: int,
                color: int
                ) -> None:
        row_bytes = color.to_bytes(self.bpp, 'little') * w
        for dy in range(h):
            off = (y + dy) * self.sl + x * self.bpp
            self.data[off:off + w * self.bpp] = row_bytes

    def clear(self) -> None:
        self.data[0:self.sl * self.h] = b'\x00' * (self.sl * self.h)

    def text(self, x: int, y: int, color: int, s: str) -> None:
        """Affiche du texte dans la fenêtre (pas dans le buffer image)."""
        self.mlx.mlx_string_put(self.mlx_ptr, self.win, x, y, color, s)

    def flush(self) -> None:
        """Envoie le buffer image vers la fenêtre."""
        self.mlx.mlx_put_image_to_window(
            self.mlx_ptr, self.win, self.img, 0, 0)

    def _loop(self, data: object) -> None:
        self.render_terminal(
                            solution_mode=self.toggle_solution,
                            wall_color=self.wall_color)
        self.flush()

    def render_terminal(
                self,
                player_pos: tuple[int, int] | None = None,
                solution_mode: bool = False,
                wall_color: int = colors.MLX_WHITE) -> None:
        now: float = time.time()
        dt: float = min(now - self.s['t_last'], 0.05)
        self.s['t_last'] = now
        self.s['elapsed'] += dt
        total_cells = self.maze.config.width * self.maze.config.height
        reveal_speed = 150  # cellules révélées par seconde
        revealed = min(int(self.s['elapsed'] * reveal_speed), total_cells)
        revealed_set = set(self.s['reveal_order'][:revealed])
        self.clear()
        px, py = player_pos if player_pos else self.maze.config.entry
        ex, ey = self.maze.config.exit
        solution: set[tuple[int, int]] = set()
        window_w = self.maze.config.window_w
        window_h = self.maze.config.window_h
        cell_w: int = window_w // self.maze.config.width
        cell_h: int = (window_h - 20) // self.maze.config.height
        wall_t: int = max(2, min(cell_w, cell_h) // 8)
        if solution_mode:
            path_str = self.maze.solve_maze(px, py, ex, ey)
            solution = self.maze._get_path_coords(px, py, path_str)
        cell_index = 0
        for y in range(self.maze.config.height):
            for x in range(self.maze.config.width):
                cell_index += 1
                cell: Cell = self.maze.grid[y][x]
                cx = x * cell_w
                cy = y * cell_h
                # Cellule pas encore révélée → gris foncé qui pulse
                if (cell_index - 1) not in revealed_set:  # pas encore révélée
                    t = self.s['elapsed'] * 3 + cell_index * .1
                    pulse = int(20 + 10 * abs(math.sin(t)))
                    self._fill_rect(
                                cx, cy, cell_w, cell_h,
                                pulse << 16 | pulse << 8 | pulse)
                    continue
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
                # Murs
                if cell.has_wall(Cell.north):
                    self._fill_rect(cx, cy, cell_w, wall_t, wall_color)
                if cell.has_wall(Cell.south):
                    self._fill_rect(
                            cx, cy + cell_h - wall_t,
                            cell_w, wall_t, wall_color)
                if cell.has_wall(Cell.west):
                    self._fill_rect(cx, cy, wall_t, cell_h, wall_color)
                if cell.has_wall(Cell.east):
                    self._fill_rect(cx + cell_w - wall_t,
                                    cy, wall_t, cell_h, wall_color)

    def draw_new_maze(self):
        self.clear()
        self.maze = MazeGenerator(self.config_path)
        self.maze.create_maze_with_bfs()
        self.s['elapsed'] = 0.0
        self.s['t_last'] = time.time()
        self.s['reveal_order'] = random.sample(
                range(
                    self.maze.config.width * self.maze.config.height),
                self.maze.config.width * self.maze.config.height
        )

    def draw_menu(self, color: int):
        pos_y = self.maze.config.window_h - 20
        pos_x = 10
        menu_1 = "regenerate[W]"
        menu_2 = "path[s]"
        menu_3 = "color[D]"
        menu_4 = "save[a]"
        menu_5 = "exit[ECHAP]"
        self.text(pos_x, pos_y, color, menu_1)
        self.text(pos_x + 140, pos_y, color, menu_2)
        self.text(pos_x + 220, pos_y, color, menu_3)
        self.text(pos_x + 310, pos_y, color, menu_4)
        self.text(pos_x + 440, pos_y, color, menu_5)

    def on_key_pressed(self, keycode: int, param: object):
        if keycode == 119:
            self.draw_new_maze()
        if keycode == 115:
            self.toggle_solution = not self.toggle_solution
        if keycode == 100:
            palette = colors.MLX_COLOR_PALETTE
            self.wall_color = palette[self.s['count'] % len(palette)]
            self.s['count'] += 1
        if keycode == 97:
            self.maze.save_maze()
        if keycode == 65307:
            self.mlx.mlx_loop_exit(self.mlx_ptr)

    def close(self, para: object) -> None:
        self.mlx.mlx_loop_exit(self.mlx_ptr), None

    def run(self) -> None:
        try:

            self.maze._embed_42_pattern()
            self.draw_new_maze()
            self.flush()
            self.draw_menu(colors.MLX_WHITE)
            self.mlx.mlx_loop_hook(self.mlx_ptr, self._loop, None)
            self.mlx.mlx_key_hook(self.win, self.on_key_pressed, None)
            self.mlx.mlx_hook(self.win, 33, 0, self.close, None)
            self.mlx.mlx_loop(self.mlx_ptr)
        except Exception as e:
            print(f"An error occured : {e}")
        finally:
            self.mlx.mlx_destroy_window(self.mlx_ptr, self.win)
            self.mlx.mlx_release(self.mlx_ptr)
