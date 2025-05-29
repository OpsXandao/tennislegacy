# main.py
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from interface.menu_inicial import menu_inicial

if __name__ == "__main__":
    menu_inicial()
