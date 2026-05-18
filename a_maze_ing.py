from mazegen.mlx_window import Renderer

if __name__ == "__main__":
    try:
        Renderer().run()
    except Exception as e:
        print(f"An error was occured {e}")
