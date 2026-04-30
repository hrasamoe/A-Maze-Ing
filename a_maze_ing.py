from mazegen.generator import MazeGenerator
from mazegen import colors
import sys


def main() -> None:
    if len(sys.argv) == 2:
        config_file: str = sys.argv[1]
    elif len(sys.argv) == 1:
        config_file = "config.txt"
        print(f"[i] No config specified. Default to '{config_file}'")
    else:
        print("Usage: python3 a_maze_ing.py [config_file]")

    try:
        maze = MazeGenerator(config_file)
        maze.create_maze_with_bfs()
        color_index = 0
        solution_mode = 0
        is_perfect = maze.config.perfect
        saved = False
        animate = False

        while True:
            palette = colors.COLOR_PALETTE
            current_color = palette[color_index % len(palette)]
            maze.render_terminal(
                solution_mode=solution_mode, wall_color=current_color)
            if is_perfect:
                perfect_str = (
                                f"\033[32mPERFECT (Single Path)"
                                f"{colors.RESET}"
                )
            else:
                perfect_str = (
                                f"{colors.YELLOW}IMPERFECT"
                                f"(Braid Path){colors.RESET}"
                )
            if animate:
                animation_str = (
                                f"\033[32m Generation Animation [True]"
                                f"{colors.RESET}"
                )
            else:
                animation_str = (
                                f"{colors.YELLOW}Generate"
                                f"Animation [False]{colors.RESET}"
                )
            save_str = f"\033[32m[Saved!]{colors.RESET}" if saved else ""

            print(f"\n{colors.WHITE}=== A-Maze-Ing Menu ==={colors.RESET}")
            print(" 1. Regenerate Maze")
            print(f" 2. Toggle Animation                 {animation_str}")
            print(" 3. Show the shortest path solution")
            print(" 4. Hide Solution Path")
            print(" 5. Change Wall Color")
            print(f" 6. Toggle Perfect Maze              {perfect_str}")
            print(f" 7. Save maze to File                {save_str}")
            print(" 8. Quit The Game")
            choice = input("Choice (1-11): ").strip()
            if choice != '6':
                saved = False
            if choice == '1':
                maze = MazeGenerator(config_file)
                maze.config.perfect = is_perfect
                maze.create_maze_with_bfs(animate)
                solution_mode = 0
            elif choice == '2':
                animate = not animate
            elif choice == '3':
                solution_mode = 1
            elif choice == '4':
                solution_mode = 0
            elif choice == '5':
                color_index += 1
            elif choice == '6':
                is_perfect = not is_perfect
            elif choice == '7':
                maze.save_maze()
                saved = True
            elif choice == '8':
                print("[+] Good Bye")
                break
            else:
                print("Please Provide a valid choice (1 - 8)")
                input()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
