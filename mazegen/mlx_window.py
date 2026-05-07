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
                't_last':  time.time(),
                'elapsed': 0.0,
                'x':       0,
                'y':       0,
                'vx':      200.0,
                'vy':      150.0,
                'angle':   0.0,
                'count': 0,
                'reveal_order': random.sample(range(total), total)
                }
        self.wall_color = colors.MLX_WHITE
        self.toggle_solution = False
        self.pos_x, self.pos_y = self.maze.config.entry
        self.game_won = False
        self.play_mod = False

    def put_pixel(self, x: int, y: int, color: int) -> None:
        if 0 <= x < self.w and 0 <= y < self.h:
            off: int = y * self.sl + x * (self.bpp)
            self.data[off:off+self.bpp] = color.to_bytes(self.bpp, 'little')

    def _try_move(self, dx: int, dy: int) -> None:
        if self.game_won:
            return

        x, y = self.pos_x, self.pos_y
        cell: Cell = self.maze.grid[y][x]
        if dx == 1 and cell.has_wall(Cell.east):
            return
        if dx == -1 and cell.has_wall(Cell.west):
            return
        if dy == -1 and cell.has_wall(Cell.north):
            return
        if dy == 1 and cell.has_wall(Cell.south):
            return
        new_x = x + dx
        new_y = y + dy
        if not (0 <= new_x < self.maze.config.width):
            return
        if not (0 <= new_y < self.maze.config.height):
            return
        self.pos_x, self.pos_y = new_x, new_y
        if (self.pos_x, self.pos_y) == self.maze.config.exit:
            self.game_won = True

    def draw_rect(
        self, x: int, y: int,
        rect_w: int, rect_h: int, color: int
    ) -> None:
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
        self.mlx.mlx_string_put(self.mlx_ptr, self.win, x, y, color, s)

    def flush(self) -> None:
        self.mlx.mlx_put_image_to_window(
            self.mlx_ptr, self.win, self.img, 0, 0)

    def _loop(self, data: object) -> None:
        self.render_terminal(
                            player_pos=(self.pos_x, self.pos_y),
                            solution_mode=self.toggle_solution,
                            wall_color=self.wall_color)
        self.flush()
        if self.game_won:
            cx = self.w // 2 - 200
            cy = self.h // 2
            self.draw_rect(cx, cy, 300, 100, colors.MLX_YELLOW)
            self.flush()
            self.text(
                    cx + 13, cy + 30,
                    colors.MLX_RED, "YOU WIN! [W]/[X] to replay")
            return

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
        temp_cell_w = self.maze.config.width
        cell_w: int = (window_w - (int(window_w * 0.2))) // temp_cell_w
        cell_h: int = window_h // self.maze.config.height
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
                if (cell_index - 1) not in revealed_set:
                    t = self.s['elapsed'] * 3 + cell_index * .1
                    pulse = int(20 + 10 * abs(math.sin(t)))
                    self._fill_rect(
                                cx, cy, cell_w, cell_h,
                                pulse << 16 | pulse << 8 | pulse)
                    continue
                # Fond
                if (x, y) == (px, py):
                    bg = colors.MLX_RED
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

    def draw_new_maze(self, algo: str = "BFS"):
        self.clear()
        self.maze = MazeGenerator(self.config_path)
        if algo == "BFS":
            self.maze.create_maze_with_bfs()
        else:
            self.maze.create_maze_with_dfs()
        self.s['elapsed'] = 0.0
        self.s['t_last'] = time.time()
        self.s['reveal_order'] = random.sample(
                range(
                    self.maze.config.width * self.maze.config.height),
                self.maze.config.width * self.maze.config.height
        )
        self.pos_x, self.pos_y = self.maze.config.entry
        self.game_won = False

    def draw_menu(self, color: int):
        pos_y = 5
        window_w = self.maze.config.window_w
        pos_x = window_w - (int(window_w * 0.2))
        menu_1 = "BFS[W]"
        menu_8 = "DFS[X]"
        menu_2 = "path[s]"
        menu_3 = "color[D]"
        menu_4 = "playMode:"
        menu_5 = "move[^v<>]"
        menu_6 = "save[a]"
        menu_7 = "exit[ECHAP]"
        self.text(pos_x, pos_y, color, menu_1)
        self.text(pos_x, pos_y + 20, color, menu_8)
        self.text(pos_x, pos_y + 40, color, menu_2)
        self.text(pos_x, pos_y + 60, color, menu_3)
        self.text(pos_x, pos_y + 80, color, menu_4)
        self.text(pos_x + 10, pos_y + 100, color, menu_5)
        self.text(pos_x, pos_y + 120, color, menu_6)
        self.text(pos_x, pos_y + 140, color, menu_7)

    def on_key_pressed(self, keycode: int, param: object):
        if keycode == 119:
            self.draw_new_maze("BFS")
        if keycode == 120:
            self.draw_new_maze("DFS")
        if keycode == 115:
            self.toggle_solution = not self.toggle_solution
        if keycode == 100:
            palette = colors.MLX_COLOR_PALETTE
            self.wall_color = palette[self.s['count'] % len(palette)]
            self.s['count'] += 1
        if keycode == 97:
            self.maze.save_maze()
        if keycode == 65362:
            self._try_move(0, -1)
        if keycode == 65364:
            self._try_move(0, 1)
        if keycode == 65361:
            self._try_move(-1, 0)
        if keycode == 65363:
            self._try_move(1, 0)
        if keycode == 112:
            self.play_mod = not self.play_mod
            self.draw_rect(
                        (self.w - (int(self.w * 0.2))),
                        5, 100, 100, colors.MLX_BLACK)
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
