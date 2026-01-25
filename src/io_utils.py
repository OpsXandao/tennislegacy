import os
from colorama import init, Fore, Style

# Initialize Colorama
init(autoreset=True)

def clear_screen():
    """Limpa a tela do terminal."""
    os.system('cls' if os.name == 'nt' else 'clear')

def safe_input(prompt):
    """Wrapper para input que encerra o programa em EOF (execucao nao interativa)."""
    try:
        return input(prompt)
    except EOFError:
        print("EOF recebido. Encerrando o jogo.")
        raise SystemExit(0)

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
