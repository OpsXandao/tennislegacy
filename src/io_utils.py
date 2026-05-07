import os
import sys
import termios
import tty
from select import select

try:
    from colorama import init, Fore, Style
except ImportError:
    # Fallback sem dependência externa: mantém API de cores funcionando.
    class _NoColor:
        def __getattr__(self, _name):
            return ""

    def init(*_args, **_kwargs):
        return None

    Fore = _NoColor()
    Style = _NoColor()

# Initialize Colorama
init(autoreset=True)


def clear_screen():
    """Limpa a tela do terminal."""
    os.system("cls" if os.name == "nt" else "clear")


def safe_input(prompt):
    """Wrapper para input que encerra o programa em EOF (execucao nao interativa)."""
    try:
        return input(prompt)
    except EOFError:
        print("EOF recebido. Encerrando o jogo.")
        raise SystemExit(0)


def kbhit():
    """Verifica se uma tecla foi pressionada (multiplataforma)."""
    if os.name == "nt":
        import msvcrt

        return msvcrt.kbhit()
    else:
        if not sys.stdin.isatty():
            return False
        return select([sys.stdin], [], [], 0) == ([sys.stdin], [], [])


def get_char_non_blocking():
    """Captura um caractere do teclado sem bloquear (multiplataforma)."""
    if os.name == "nt":
        import msvcrt

        return msvcrt.getch().decode("utf-8")
    else:
        if not sys.stdin.isatty():
            return ""
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setcbreak(fd)
            return sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


def print_red(text):
    print(Fore.RED + text)


def print_green(text):
    print(Fore.GREEN + text)


def print_yellow(text):
    print(Fore.YELLOW + text)


def print_blue(text):
    print(Fore.BLUE + text)


def print_magenta(text):
    print(Fore.MAGENTA + text)


def print_cyan(text):
    print(Fore.CYAN + text)


def print_bold(text):
    print(Style.BRIGHT + text)
