"""Machine Configuration Validator package."""

import importlib.util
import shutil
import subprocess
import sys


def is_poetry_available() -> bool:
    if shutil.which("poetry"):
        return True

    poetry_spec = importlib.util.find_spec("poetry")
    return poetry_spec is not None


def install_poetry() -> None:
    print("Poetry não encontrado. Instalando Poetry...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "poetry"])
        print("Poetry instalado com sucesso.")
    except subprocess.CalledProcessError as exc:
        print(f"Falha ao instalar Poetry: {exc}")
        sys.exit(1)


def main() -> None:
    if not is_poetry_available():
        install_poetry()
    else:
        print("Poetry já está instalado.")


if __name__ == "__main__":
    main()
