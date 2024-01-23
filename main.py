import os
import sys
import traceback

from gui.app import App


def clear() -> None:
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")


def exit_program() -> None:
    sys.exit(0)


def main() -> None:
    try:
        app = App()
        app.mainloop()
        exit_program()
    except Exception as exception:
        print("\nError:", exception)
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
