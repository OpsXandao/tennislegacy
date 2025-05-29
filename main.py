import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "src"))  # noqa: E402

from interface.menu_inicial import menu_inicial

if __name__ == "__main__":
    menu_inicial()
